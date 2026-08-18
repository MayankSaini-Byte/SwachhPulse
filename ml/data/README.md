# SwachhPulse — Data Directory

## Purpose

This directory stores all datasets used by the SwachhPulse platform.
Every file here must maintain clear provenance and labeling.

---

## Directory Structure

```text
data/
├── raw/                    # Untouched downloaded files — NEVER modify these
│   ├── municipal/          # Municipal complaints, ward stats, collection records
│   ├── waste/              # Solid waste generation, processing, weighbridge data
│   ├── sanitation/         # Sanitation reports, open-defecation surveys
│   ├── weather/            # Rainfall, temperature, humidity datasets
│   ├── gis/                # Ward boundaries, shapefiles, OpenStreetMap extracts
│   ├── demographics/       # Population, household, census data
│   └── other/              # Any dataset that doesn't fit above categories
│
├── synthetic/              # Clearly labeled synthetic/demo data for development
│   └── README.md
│
├── manifests/              # Dataset provenance manifests (datasets.json)
│   └── datasets.json
│
└── README.md               # This file
```

---

## Data Classification Rules

From `SwachhPulse.md`:

| Label          | Meaning                                              |
|----------------|------------------------------------------------------|
| **REAL DATA**      | Actual downloaded public/government datasets     |
| **SYNTHETIC DATA** | Generated for development/testing — clearly marked |
| **DEMO DATA**      | Sample data for demonstrations — clearly marked  |

> **IMPORTANT**: Never claim synthetic or demo observations are real data.

---

## Raw Data Policy

All files inside `raw/` **must remain untouched** after download.

- No column renaming
- No null removal
- No datatype casting
- No deduplication
- No normalization
- No feature engineering

If validation metadata is needed, store it in `manifests/`, NOT in the raw file.

---

## Provenance

Every downloaded dataset must have a corresponding entry in:

```
data/manifests/datasets.json
```

Each entry records:
- Dataset ID
- Title
- Source and URL
- Download timestamp
- Local file path
- Format (CSV, JSON, etc.)
- File size in bytes
- SHA-256 checksum
- License information
- Description
- Download status

---

## Priority Data Sources (India-focused)

1. Government Open Data Platform (data.gov.in)
2. State government open-data portals
3. Municipal corporation datasets
4. Central Pollution Control Board (CPCB)
5. India Meteorological Department (IMD)
6. Census of India
7. OpenStreetMap
8. Swachh Bharat Mission reports
9. Municipal solid waste statistics
10. Ward-level collection and complaint data

---

## Duplicate Handling

- SHA-256 checksums prevent blind overwrites
- Updated versions get date-suffixed filenames (e.g., `dataset_2026-08-18.csv`)
- The manifest tracks all versions
