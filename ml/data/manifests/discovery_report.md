# WebReaper Discovery Report

> Generated: 2026-08-18

## Discovery Methodology

Each candidate dataset was evaluated against these criteria:
1. **Has location?** (lat/lon, ward, city, district)
2. **Has date/time?** (timestamp, date column)
3. **Contains sanitation/waste variable?** (complaint type, waste metrics)
4. **Can become target variable?** (for hotspot prediction)
5. **Can join with weather data?** (shared city + date)

Priority: datasets containing BOTH **location + time** for spatiotemporal prediction.

---

## Sources Discovered & Evaluated

### DOWNLOADED (Verified & Collected)

| Source | Dataset | Location | Time | Sanitation Var | Target Var | Weather Join | Status |
|--------|---------|----------|------|----------------|-----------|--------------|--------|
| OpenCity.in/BBMP | Grievances 2020-2025 | Ward name | Timestamp | YES (categories) | YES | YES (Bangalore) | DOWNLOADED |
| Open-Meteo | Weather 6 cities | Lat/lon | Daily | NO (predictor) | NO | IS weather | DOWNLOADED |
| OpenCity.in/MoHUA | Swachh Survekshan 2024-25 | City | Annual | YES (scores) | NO | Indirect | DOWNLOADED |
| GitHub/Census | Census 2011 Districts | District | 2011 | Partial (sanitation infra) | NO | NO | DOWNLOADED |
| GitHub/geohacker | India States GeoJSON | Polygons | N/A | NO | NO | NO | DOWNLOADED |

### BLOCKED / AUTH REQUIRED

| Source | Dataset | Reason | Action |
|--------|---------|--------|--------|
| data.gov.in | Solid Waste Management CSV | 403 Forbidden | Needs API key registration |
| CPCB | Annual Waste Reports | PDF only, no CSV | Manual extraction needed |
| Dataful.in | State-wise Waste Stats | No direct CSV URL, requires browser | Consider Selenium/manual |
| CPCB AQI API | Air Quality Index | Requires registration | Register for API key |
| Kaggle | Waste Management Indian Cities | Requires Kaggle auth | Manual download via Kaggle CLI |
| Kaggle | Swachh Survekshan full history | Requires Kaggle auth | Manual download via Kaggle CLI |

### EVALUATED BUT NOT COLLECTED (Low Priority)

| Source | Dataset | Reason Not Collected |
|--------|---------|---------------------|
| Overpass API | Bengaluru waste bins | Low OSM coverage for waste infrastructure |
| IMD | Detailed meteorological data | Requires institutional access |
| Census India | Ward-level population | Available only as Excel/PDF on official site |
| SBM Urban | ODF status by city | Dashboard only, no CSV export |

---

## Key Dataset: BBMP Grievances (Primary ML Data)

**Why this is the most important dataset for SwachhPulse:**

1. **766,648 total records** across 6 years (2020-2025)
2. **Ward-level granularity** -- Bengaluru's ~198 wards
3. **Daily timestamps** -- can compute daily incident counts per ward
4. **Complaint categories** include:
   - Solid Waste (Garbage) Related
   - Drain/Storm Water Drain
   - Road/Footpath related
   - Electrical
   - Public Health
   - Tree related
   - And more
5. **Resolution tracking** -- Grievance Status (Open/Closed)
6. **Directly maps to SwachhPulse prediction target**:
   ```
   Will ward X have a sanitation incident tomorrow?
   = Will there be a complaint filed for ward X on date Y?
   ```
7. **Joinable with Bangalore weather data** for feature enrichment

### Suggested ML Feature Pipeline
```
BBMP Grievances (ward, date, category)
    + Weather (date, temp, rain)
    + Census (district demographics)
    --> ward_day features
    --> hotspot risk prediction
```

---

## Manifest Summary

- Total datasets: 16
- Total size: 129.5 MB
- All 16/16 SHA-256 checksum verified
- Manifest: data/manifests/datasets.json
