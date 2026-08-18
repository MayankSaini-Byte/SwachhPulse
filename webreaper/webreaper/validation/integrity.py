"""
Basic integrity checks for downloaded files.

ONLY validation — no cleaning, no modification, no transformation.
Results go into metadata, never into the raw file.
"""

import logging
from pathlib import Path
from typing import Dict

from webreaper.downloader.csv_dl import detect_csv_properties

logger = logging.getLogger("webreaper.validation")


def validate_file(filepath: Path) -> Dict:
    """
    Run basic integrity checks on a downloaded file.
    
    Allowed checks:
    - File exists
    - File is not empty
    - For CSV: can be opened, detect delimiter/encoding/rows/columns
    - Detect obvious malformed downloads (HTML pretending to be CSV)
    
    NOT allowed:
    - Removing nulls, changing columns, dropping duplicates, etc.
    """
    result = {
        "filepath": str(filepath),
        "exists": False,
        "size_bytes": 0,
        "is_empty": True,
        "format_detected": None,
        "validation_passed": False,
        "details": {},
        "errors": [],
    }

    if not filepath.exists():
        result["errors"].append("File does not exist")
        return result

    result["exists"] = True
    result["size_bytes"] = filepath.stat().st_size
    result["is_empty"] = result["size_bytes"] == 0

    if result["is_empty"]:
        result["errors"].append("File is empty (0 bytes)")
        return result

    suffix = filepath.suffix.lower()

    # CSV validation
    if suffix in (".csv", ".tsv"):
        result["format_detected"] = "csv"
        csv_info = detect_csv_properties(filepath)
        result["details"] = csv_info

        if csv_info["is_valid_csv"]:
            result["validation_passed"] = True
            logger.info(
                f"[VALIDATE] {filepath.name}: CSV OK — "
                f"{csv_info['num_rows']} rows, {csv_info['num_columns']} cols, "
                f"delimiter='{csv_info['delimiter']}', encoding={csv_info['encoding']}"
            )
        else:
            result["errors"].append(csv_info.get("error", "CSV validation failed"))
            logger.warning(f"[VALIDATE] {filepath.name}: CSV FAILED — {csv_info.get('error')}")

    # JSON validation
    elif suffix == ".json":
        result["format_detected"] = "json"
        try:
            import json
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            result["validation_passed"] = True
            if isinstance(data, list):
                result["details"]["num_records"] = len(data)
            elif isinstance(data, dict):
                result["details"]["top_level_keys"] = list(data.keys())[:20]
            logger.info(f"[VALIDATE] {filepath.name}: JSON OK")
        except json.JSONDecodeError as e:
            result["errors"].append(f"Invalid JSON: {e}")
            logger.warning(f"[VALIDATE] {filepath.name}: JSON FAILED — {e}")

    # ZIP validation
    elif suffix == ".zip":
        result["format_detected"] = "zip"
        import zipfile
        if zipfile.is_zipfile(filepath):
            result["validation_passed"] = True
            with zipfile.ZipFile(filepath, "r") as zf:
                result["details"]["files"] = zf.namelist()[:50]
                result["details"]["num_files"] = len(zf.namelist())
            logger.info(f"[VALIDATE] {filepath.name}: ZIP OK — {result['details']['num_files']} files")
        else:
            result["errors"].append("Not a valid ZIP file")

    # XLSX validation
    elif suffix in (".xlsx", ".xls"):
        result["format_detected"] = "xlsx"
        result["validation_passed"] = True  # Basic check — file exists and is not empty
        logger.info(f"[VALIDATE] {filepath.name}: XLSX — {result['size_bytes']} bytes")

    # GeoJSON
    elif suffix == ".geojson":
        result["format_detected"] = "geojson"
        try:
            import json
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("type") in ("FeatureCollection", "Feature", "GeometryCollection"):
                result["validation_passed"] = True
                if "features" in data:
                    result["details"]["num_features"] = len(data["features"])
                logger.info(f"[VALIDATE] {filepath.name}: GeoJSON OK")
            else:
                result["errors"].append("JSON file but not valid GeoJSON")
        except Exception as e:
            result["errors"].append(f"GeoJSON error: {e}")

    else:
        # Unknown format — basic checks only
        result["format_detected"] = suffix.lstrip(".")
        result["validation_passed"] = True  # It exists and is not empty
        logger.info(f"[VALIDATE] {filepath.name}: Unknown format, basic check passed")

    return result
