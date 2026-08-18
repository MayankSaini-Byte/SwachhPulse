"""
Manifest management — tracks dataset provenance.

Every downloaded file gets an entry in data/manifests/datasets.json
recording source, checksum, timestamp, and validation results.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict

from webreaper.config import get_settings
from webreaper.utils.hashing import compute_sha256

logger = logging.getLogger("webreaper.metadata")


class ManifestManager:
    """Manages the datasets.json manifest file."""

    def __init__(self, manifest_path: Optional[Path] = None):
        settings = get_settings()
        self.manifest_path = manifest_path or (settings.manifest_dir / "datasets.json")
        self._ensure_manifest()

    def _ensure_manifest(self):
        """Create manifest file if it doesn't exist."""
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.manifest_path.exists():
            self._write({
                "manifest_version": "1.0",
                "project": "SwachhPulse",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "description": "Dataset provenance manifest for all downloaded/collected data files.",
                "datasets": [],
            })

    def _read(self) -> dict:
        """Read manifest from disk."""
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: dict):
        """Write manifest to disk."""
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_entry(
        self,
        dataset_id: str,
        title: str,
        source: str,
        source_url: str,
        local_path: Path,
        format: str,
        license: str = "unknown",
        description: str = "",
        category: str = "other",
        validation_result: Optional[dict] = None,
    ) -> dict:
        """
        Add a new dataset entry to the manifest.
        
        Computes SHA-256 and records full provenance.
        """
        manifest = self._read()

        # Compute checksum
        sha256 = compute_sha256(local_path)
        size_bytes = local_path.stat().st_size

        # Check for duplicate (same SHA-256)
        for existing in manifest["datasets"]:
            if existing.get("sha256") == sha256:
                logger.info(f"[MANIFEST] Duplicate detected (same SHA-256): {title}")
                return existing

        entry = {
            "dataset_id": dataset_id,
            "title": title,
            "source": source,
            "source_url": source_url,
            "downloaded_at": datetime.now(timezone.utc).isoformat(),
            "local_path": str(local_path),
            "format": format,
            "size_bytes": size_bytes,
            "sha256": sha256,
            "license": license,
            "description": description,
            "category": category,
            "status": "downloaded",
            "validation": validation_result,
        }

        manifest["datasets"].append(entry)
        self._write(manifest)

        logger.info(f"[MANIFEST] Added: {title} ({size_bytes} bytes, SHA256: {sha256[:16]}...)")
        return entry

    def get_all(self) -> List[dict]:
        """Get all dataset entries."""
        return self._read().get("datasets", [])

    def find_by_sha256(self, sha256: str) -> Optional[dict]:
        """Find a dataset by its SHA-256 hash."""
        for entry in self.get_all():
            if entry.get("sha256") == sha256:
                return entry
        return None

    def find_by_url(self, url: str) -> Optional[dict]:
        """Find a dataset by its source URL."""
        for entry in self.get_all():
            if entry.get("source_url") == url:
                return entry
        return None

    def verify_all(self) -> List[dict]:
        """Verify integrity of all downloaded files."""
        results = []
        for entry in self.get_all():
            path = Path(entry["local_path"])
            result = {
                "dataset_id": entry["dataset_id"],
                "title": entry["title"],
                "path": entry["local_path"],
                "exists": path.exists(),
                "checksum_match": False,
            }
            if path.exists():
                current_hash = compute_sha256(path)
                result["checksum_match"] = current_hash == entry.get("sha256")
                result["current_sha256"] = current_hash
                result["recorded_sha256"] = entry.get("sha256")
            results.append(result)
        return results

    def summary(self) -> dict:
        """Get a summary of the manifest."""
        datasets = self.get_all()
        categories = {}
        total_size = 0
        for d in datasets:
            cat = d.get("category", "other")
            categories[cat] = categories.get(cat, 0) + 1
            total_size += d.get("size_bytes", 0)

        return {
            "total_datasets": len(datasets),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "categories": categories,
        }
