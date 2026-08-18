"""
WebReaper collection script — Phase 3: Waste, Demographics, GIS, Swachh Survekshan.

All URLs verified via web search and API probing.
"""

import sys
import os
import time
import json
import logging

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


DATASETS = [
    # ----- CATEGORY 2: WASTE DATA -----
    # Swachh Survekshan 2024-25 cleanliness rankings (Million+ cities)
    # Source: OpenCity.in — verified download URL from search
    # Contains: City rankings, scores, ODF status, waste management metrics
    # Spatiotemporal: YES (city = location, survey year = time)
    # Sanitation variable: YES (cleanliness scores, waste management scores)
    # Can join with weather: YES (city-level)
    {
        "dataset_id": "swachh-survekshan-2024-million-plus",
        "title": "Swachh Survekshan 2024-25 Rankings (Million+ Cities)",
        "source": "OpenCity.in / MoHUA",
        "source_url": "https://data.opencity.in/dataset/4d4028fe-afed-4b7d-a5de-3b9ff5df8662",
        "download_url": "https://data.opencity.in/dataset/4d4028fe-afed-4b7d-a5de-3b9ff5df8662/resource/0e6e43e6-439d-4b07-b304-b718624c2abc/download/82e5386e-97ca-47bc-bf3a-52f376c21e63.csv",
        "format": "csv",
        "description": "Swachh Survekshan 2024-25 city cleanliness rankings for Million+ population cities. Includes total scores, ODF status, waste segregation metrics.",
        "license": "Public Domain",
        "category": "waste",
    },
    # Swachh Survekshan 2024-25 (3L-1M cities)
    {
        "dataset_id": "swachh-survekshan-2024-3l-1m",
        "title": "Swachh Survekshan 2024-25 Rankings (3 Lakh to 1 Million Cities)",
        "source": "OpenCity.in / MoHUA",
        "source_url": "https://data.opencity.in/dataset/4d4028fe-afed-4b7d-a5de-3b9ff5df8662",
        "download_url": "https://data.opencity.in/dataset/4d4028fe-afed-4b7d-a5de-3b9ff5df8662/resource/fc57bb8b-8f53-48af-a909-4d5cfe461b46/download/ecb2e925-a68f-4f22-b1dc-22c948c61092.csv",
        "format": "csv",
        "description": "Swachh Survekshan 2024-25 city cleanliness rankings for 3 Lakh to 1 Million population cities.",
        "license": "Public Domain",
        "category": "waste",
    },

    # ----- CATEGORY 3: DEMOGRAPHICS -----
    # India Census 2011 district-level data from GitHub (well-known public dataset)
    # Contains: District, State, Population, Male, Female, Literate, etc.
    # Spatiotemporal: YES (district = location)
    # Can join: YES (district/state level)
    {
        "dataset_id": "india-census-2011-districts",
        "title": "India Census 2011 District-wise Population and Demographics",
        "source": "GitHub (nishusharma1608/India-Census-2011-Analysis)",
        "source_url": "https://github.com/nishusharma1608/India-Census-2011-Analysis",
        "download_url": "https://raw.githubusercontent.com/nishusharma1608/India-Census-2011-Analysis/master/india-districts-census-2011.csv",
        "format": "csv",
        "description": "District-wise population, sex ratio, literacy, workers, and demographic indicators from India Census 2011. 640 districts.",
        "license": "Public Domain (Census of India)",
        "category": "demographics",
    },

    # ----- CATEGORY 4: GIS -----
    # India state boundaries GeoJSON — commonly available
    {
        "dataset_id": "india-states-geojson",
        "title": "India State Boundaries GeoJSON",
        "source": "GitHub (Subhash9325/GeospatialData)",
        "source_url": "https://github.com/Subhash9325/GeoJSON-India",
        "download_url": "https://raw.githubusercontent.com/Subhash9325/GeoJSON-India/master/India_States.geojson",
        "format": "geojson",
        "description": "State-level administrative boundaries for India in GeoJSON format. For map visualization and spatial joins.",
        "license": "Open Data",
        "category": "gis",
    },
]


def main():
    settings = get_settings()
    manifest = ManifestManager()
    session = create_session()

    print(f"\n{'='*70}")
    print(f"  WEBREAPER PHASE 3 — Waste, Demographics, GIS Data")
    print(f"  {len(DATASETS)} datasets queued")
    print(f"{'='*70}\n")

    success = 0
    failed = 0
    skipped = 0

    for ds in DATASETS:
        cat = ds["category"]
        cat_dir = ensure_dir(settings.raw_dir / cat)
        filename = sanitize_filename(f"{ds['dataset_id']}.{ds['format']}")
        dest = cat_dir / filename

        print(f"  [{cat.upper()}] {ds['title']}")
        print(f"    Source: {ds['source']}")

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
                fmt = val.get("format_detected", ds["format"])
                if fmt == "geojson":
                    features = details.get("num_features", "?")
                    print(f"    [OK] Validated: GeoJSON with {features} features")
                else:
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

        time.sleep(1.5)

    print(f"{'='*70}")
    print(f"  Phase 3 Complete: {success} downloaded, {failed} failed, {skipped} skipped")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
