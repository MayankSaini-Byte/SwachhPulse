"""
WebReaper collection script — Phase 2: Non-weather datasets.

Downloads verified public datasets for SwachhPulse categories:
1. Municipal/Sanitation (BBMP Grievances from OpenCity.in)
2. Waste/Collection
3. Demographics
4. GIS/Spatial
5. Environmental

Uses WebReaper downloader infrastructure directly.
"""

import sys
import os
import time
import json
import logging

# Add webreaper to path
sys.path.insert(0, os.path.dirname(__file__))

from webreaper.config import get_settings
from webreaper.downloader.http import stream_download, create_session
from webreaper.validation.integrity import validate_file
from webreaper.metadata.manifest import ManifestManager
from webreaper.utils.filesystem import sanitize_filename, versioned_path, ensure_dir
from webreaper.utils.hashing import compute_sha256

import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("webreaper.collect")


# ============================================================
# VERIFIED DATASETS — All URLs confirmed via API/web search
# ============================================================

DATASETS_TO_COLLECT = [
    # ----- CATEGORY 1: MUNICIPAL / SANITATION INCIDENT DATA -----
    # Source: OpenCity.in CKAN API — BBMP Bengaluru Ward-level Grievances
    # Verified via: https://data.opencity.in/api/3/action/package_search?q=BBMP+grievances
    # Contains: Complaint ID, Category, Sub Category, Grievance Date, Ward Name, Status
    # Spatiotemporal: YES (ward = location, grievance date = time)
    # Sanitation variable: YES (complaint categories include garbage, sanitation)
    # Can join with weather: YES (date + Bangalore city)
    {
        "dataset_id": "bbmp-grievances-2024",
        "title": "BBMP Bengaluru Ward-level Grievances 2024",
        "source": "OpenCity.in / BBMP",
        "source_url": "https://data.opencity.in/dataset/bbmp-grievances-data",
        "download_url": "https://data.opencity.in/dataset/54344a76-a37a-4d05-961c-df9bac5494ad/resource/2a3f29ef-a7a1-4fc3-b125-cbcc958a89d1/download/82f88d50-71c5-4203-92ac-5ccb5cabc7a2.csv",
        "format": "csv",
        "description": "Ward-level grievances filed in 2024 with BBMP Bengaluru. Includes complaint ID, category, sub-category, grievance date, ward name, status, staff remarks.",
        "license": "Public Domain",
        "category": "municipal",
        "expected_size": 28098048,
        "notes": "HIGHEST PRIORITY. 28 MB. Spatiotemporal: ward + date. Direct target variable for hotspot prediction.",
    },
    {
        "dataset_id": "bbmp-grievances-2023",
        "title": "BBMP Bengaluru Ward-level Grievances 2023",
        "source": "OpenCity.in / BBMP",
        "source_url": "https://data.opencity.in/dataset/bbmp-grievances-data",
        "download_url": "https://data.opencity.in/dataset/54344a76-a37a-4d05-961c-df9bac5494ad/resource/fae120ab-d95c-4281-aa86-5bf694712472/download/d4419a76-e2af-44b3-aa25-369c85126f0f.csv",
        "format": "csv",
        "description": "Ward-level grievances filed in 2023 with BBMP Bengaluru.",
        "license": "Public Domain",
        "category": "municipal",
        "expected_size": 15892656,
        "notes": "16 MB. Same schema as 2024.",
    },
    {
        "dataset_id": "bbmp-grievances-2022",
        "title": "BBMP Bengaluru Ward-level Grievances 2022",
        "source": "OpenCity.in / BBMP",
        "source_url": "https://data.opencity.in/dataset/bbmp-grievances-data",
        "download_url": "https://data.opencity.in/dataset/54344a76-a37a-4d05-961c-df9bac5494ad/resource/e44f1808-4923-4390-b62c-710d19ab876b/download/b4dd8dd1-1628-4f35-9247-ef5afaad214d.csv",
        "format": "csv",
        "description": "Ward-level grievances filed in 2022 with BBMP Bengaluru.",
        "license": "Public Domain",
        "category": "municipal",
        "expected_size": 16082496,
        "notes": "16 MB. Same schema as 2024.",
    },
    {
        "dataset_id": "bbmp-grievances-2025",
        "title": "BBMP Bengaluru Ward-level Grievances 2025 (partial, until June 2025)",
        "source": "OpenCity.in / BBMP",
        "source_url": "https://data.opencity.in/dataset/bbmp-grievances-data",
        "download_url": "https://data.opencity.in/dataset/54344a76-a37a-4d05-961c-df9bac5494ad/resource/1342a93b-9a61-4766-9c34-c8357b7926c2/download/b0d6e9ff-5eef-48bf-ba86-985dbe8112d1.csv",
        "format": "csv",
        "description": "Ward-level grievances filed in 2025 (until June 19th 2025) with BBMP Bengaluru.",
        "license": "Public Domain",
        "category": "municipal",
        "expected_size": 18272067,
        "notes": "18 MB. Partial year data.",
    },
    {
        "dataset_id": "bbmp-grievances-2021",
        "title": "BBMP Bengaluru Ward-level Grievances 2021",
        "source": "OpenCity.in / BBMP",
        "source_url": "https://data.opencity.in/dataset/bbmp-grievances-data",
        "download_url": "https://data.opencity.in/dataset/54344a76-a37a-4d05-961c-df9bac5494ad/resource/bada528d-f4f5-4ace-9dd1-8ac459fe350b/download/9e7e6892-06b6-4fdc-967a-e4787562f155.csv",
        "format": "csv",
        "description": "Ward-level grievances filed in 2021 with BBMP Bengaluru.",
        "license": "Public Domain",
        "category": "municipal",
        "expected_size": 14323109,
        "notes": "14 MB. Same schema as 2024.",
    },
    {
        "dataset_id": "bbmp-grievances-2020",
        "title": "BBMP Bengaluru Ward-level Grievances 2020 (from Feb 8th)",
        "source": "OpenCity.in / BBMP",
        "source_url": "https://data.opencity.in/dataset/bbmp-grievances-data",
        "download_url": "https://data.opencity.in/dataset/54344a76-a37a-4d05-961c-df9bac5494ad/resource/58808356-4b0a-4b02-9d70-75993b4dcd1c/download/413fa9ec-8d06-4ecb-884e-1436c5a0f5dd.csv",
        "format": "csv",
        "description": "Ward-level grievances filed in 2020 (from Feb 8th) with BBMP Bengaluru.",
        "license": "Public Domain",
        "category": "municipal",
        "expected_size": 13037238,
        "notes": "13 MB. Starts from Feb 2020.",
    },
]


def main():
    settings = get_settings()
    manifest = ManifestManager()
    session = create_session()

    print(f"\n{'='*70}")
    print(f"  WEBREAPER PHASE 2 — Non-weather Data Collection")
    print(f"  {len(DATASETS_TO_COLLECT)} datasets queued")
    print(f"{'='*70}\n")

    success = 0
    failed = 0
    skipped = 0

    for ds in DATASETS_TO_COLLECT:
        cat = ds["category"]
        cat_dir = ensure_dir(settings.raw_dir / cat)
        filename = sanitize_filename(f"{ds['dataset_id']}.{ds['format']}")
        dest = cat_dir / filename

        print(f"  [{cat.upper()}] {ds['title']}")
        print(f"    Source: {ds['source']}")
        print(f"    Expected: ~{ds.get('expected_size', 0) // 1024} KB")

        # Check existing
        if dest.exists() and not settings.overwrite:
            existing_hash = compute_sha256(dest)
            if manifest.find_by_sha256(existing_hash):
                print(f"    [SKIP] Already downloaded.\n")
                skipped += 1
                continue
            else:
                dest = versioned_path(dest)

        # Download
        ok, msg = stream_download(ds["download_url"], dest, session)

        if ok:
            print(f"    [OK] {msg}")

            # Validate
            val = validate_file(dest)
            if val["validation_passed"]:
                details = val.get("details", {})
                rows = details.get("num_rows", "?")
                cols = details.get("num_columns", "?")
                print(f"    [OK] Validated: {rows} rows, {cols} cols")
            else:
                print(f"    [WARN] Validation issues: {val.get('errors', [])}")

            # Manifest
            manifest.add_entry(
                dataset_id=ds["dataset_id"],
                title=ds["title"],
                source=ds["source"],
                source_url=ds["download_url"],
                local_path=dest,
                format=ds["format"],
                license=ds["license"],
                description=ds["description"],
                category=ds["category"],
                validation_result=val,
            )
            print(f"    [OK] Manifest updated")
            print(f"    Saved: {dest}\n")
            success += 1
        else:
            print(f"    [FAIL] {msg}\n")
            failed += 1

        # Polite delay
        time.sleep(2)

    print(f"{'='*70}")
    print(f"  Phase 2 Complete: {success} downloaded, {failed} failed, {skipped} skipped")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
