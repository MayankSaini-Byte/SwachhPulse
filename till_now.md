# SwachhPulse -- Progress Log (till_now.md)

> Last updated: 2026-08-18T17:38+05:30

---

## Project Overview

**SwachhPulse** is a student-built civic-tech prototype for **SIH1322 -- Domestic Waste Management**.

**Goal**: Build a working system that accepts citizen sanitation reports, stores location/time/evidence, uses AI for report understanding, predicts sanitation hotspots via ML, and displays everything on a dashboard with a sanitation score.

**Core loop**:
```
Citizen Report -> FastAPI -> LLM/NLP -> Structured Incident -> PostgreSQL/PostGIS -> ML Risk Model -> Sanitation Index -> Dashboard
```

---

## DATA STATUS

### Weather: COMPLETE (6 datasets)

| Dataset | City | Rows | Cols | Size | Source |
|---------|------|------|------|------|--------|
| openmeteo-delhi-historical | Delhi | 2,195 | 6 | 72 KB | Open-Meteo |
| openmeteo-mumbai-historical | Mumbai | 2,195 | 6 | 73 KB | Open-Meteo |
| openmeteo-bangalore-historical | Bangalore | 2,195 | 6 | 73 KB | Open-Meteo |
| openmeteo-chennai-historical | Chennai | 2,195 | 6 | 73 KB | Open-Meteo |
| openmeteo-kolkata-historical | Kolkata | 2,195 | 6 | 73 KB | Open-Meteo |
| openmeteo-hyderabad-historical | Hyderabad | 2,195 | 6 | 72 KB | Open-Meteo |

**Fields**: date, temperature_2m_max, temperature_2m_min, precipitation_sum, rain_sum, weathercode  
**Period**: 2020-01-01 to 2025-12-31  
**License**: CC-BY 4.0  
**Spatiotemporal**: YES (lat/lon embedded in header, daily dates)

---

### Municipal/Sanitation: COMPLETE (6 datasets) -- HIGHEST PRIORITY DATA

| Dataset | Year | Rows | Cols | Size | Source |
|---------|------|------|------|------|--------|
| bbmp-grievances-2020 | 2020 (from Feb) | 91,620 | 8 | 13 MB | OpenCity.in/BBMP |
| bbmp-grievances-2021 | 2021 | 103,504 | 8 | 14 MB | OpenCity.in/BBMP |
| bbmp-grievances-2022 | 2022 | 118,394 | 8 | 16 MB | OpenCity.in/BBMP |
| bbmp-grievances-2023 | 2023 | 119,140 | 8 | 16 MB | OpenCity.in/BBMP |
| bbmp-grievances-2024 | 2024 | 207,016 | 8 | 28 MB | OpenCity.in/BBMP |
| bbmp-grievances-2025 | 2025 (to June) | 126,974 | 8 | 18 MB | OpenCity.in/BBMP |

**Total**: 766,648 complaint records across 6 years  
**Fields**: Complaint ID, Category, Sub Category, Grievance Date, Ward Name, Grievance Status, Staff Remarks, Staff Name  
**License**: Public Domain  
**Spatiotemporal**: YES  
- **Location**: Ward Name (Bengaluru BBMP wards)  
- **Time**: Grievance Date (full timestamp)  
- **Sanitation variable**: YES -- Category includes "Solid Waste (Garbage) Related", "Drain/Storm Water Drain", sanitation categories  
- **Target variable potential**: YES -- can predict "will a complaint occur in ward X on day Y?"  
- **Joinable with weather**: YES -- Bangalore weather data available (same city, same time range)  
- **Resolution tracking**: YES -- Grievance Status (Open/Closed), Staff Remarks

This is the **primary ML training data** for hotspot prediction.

---

### Waste/Collection: PARTIAL (2 datasets)

| Dataset | Rows | Cols | Size | Source |
|---------|------|------|------|--------|
| swachh-survekshan-2024-million-plus | 40 | 7 | 2 KB | OpenCity.in/MoHUA |
| swachh-survekshan-2024-3l-1m | 95 | 7 | 4 KB | OpenCity.in/MoHUA |

**Fields**: Rank, State/UT Name, ULB Name, Total Score, SS2024 Score, SS2025 Score, ODF Score  
**License**: Public Domain  
**Spatiotemporal**: PARTIAL (city-level, annual)  
**Use case**: City-level waste management benchmarking, not granular enough for ward-level prediction  

**Blocked sources**:
- data.gov.in Solid Waste CSV: AUTH_REQUIRED (403 Forbidden -- needs API key or URL update)
- CPCB waste reports: Available as PDF only, not CSV
- Dataful.in: Requires browser interaction, no direct CSV URL found

---

### Demographics: COMPLETE (1 dataset)

| Dataset | Rows | Cols | Size | Source |
|---------|------|------|------|--------|
| india-census-2011-districts | 640 | 118 | 448 KB | GitHub/Census |

**Fields**: District code, State name, District name, Population, Male, Female, Literate, SC/ST, Workers, Households, Housing conditions, Sanitation (latrine type, drainage, water source), Power parity, etc.  
**License**: Public Domain (Census of India)  
**Spatiotemporal**: YES (district-level, 2011 snapshot)  
**Use case**: Population density context for hotspot prediction, sanitation infrastructure baseline, joining with ward-level data  
**Notable columns for SwachhPulse**: Having_latrine_facility, Not_having_latrine_facility, Household water sources, LPG usage, Condition of houses  

---

### GIS/Spatial: PARTIAL (1 dataset)

| Dataset | Features | Size | Source |
|---------|----------|------|--------|
| india-states-geojson | 35 states/UTs | 23 MB | GitHub (geohacker/india) |

**Format**: GeoJSON  
**License**: Open Data  
**Use case**: State-level map visualization, dashboard backgrounds  
**Limitation**: State-level only. Ward boundaries for Bengaluru not yet collected.

**Blocked/not found**:
- BBMP ward boundaries GeoJSON: Not found as direct public download. May exist on OpenCity.in or need Overpass API query.
- Bengaluru waste infrastructure (bins, collection points): Available via Overpass API but needs manual query execution

---

### Other/Environmental: NOT COLLECTED

**Rationale**: Weather data already covers temperature and precipitation for 6 cities. Additional AQI/humidity data is lower priority since:
1. The primary prediction target is sanitation complaints (covered by BBMP data)
2. Weather correlation is already possible with current data
3. CPCB AQI API exists but requires registration

**Potential future sources**:
- CPCB AQI API: REQUIRES_REGISTRATION
- Flood/drainage data: Not found as public CSV

---

## Collection Summary

| Category | Datasets | Records | Total Size | Status |
|----------|----------|---------|------------|--------|
| Weather | 6 | 13,170 | 436 KB | COMPLETE |
| Municipal/Sanitation | 6 | 766,648 | 105 MB | COMPLETE |
| Waste/Collection | 2 | 135 | 6 KB | PARTIAL |
| Demographics | 1 | 640 | 448 KB | COMPLETE |
| GIS/Spatial | 1 | 35 features | 23 MB | PARTIAL |
| Other/Environmental | 0 | -- | -- | NOT COLLECTED |
| **TOTAL** | **16** | **780,628** | **129.5 MB** | -- |

All 16 datasets: **16/16 SHA-256 checksum verified**

---

## What Has Been Done So Far

### 1. Project Specification & Planning (DONE)
- SwachhPulse.md -- Full project spec finalized
- scrapper.md -- WebReaper collector spec finalized

### 2. WebReaper Implementation (DONE)
- Full Python package with 7 CLI commands
- Discovery engine (CKAN API + known datasets)
- Streaming downloader with retry, HTML detection, size limits
- SHA-256 provenance tracking
- CSV/JSON/ZIP/GeoJSON validation

### 3. Data Collection -- 3 Phases (DONE)
- Phase 1: Weather data (6 cities, Open-Meteo API)
- Phase 2: Municipal grievances (BBMP Bengaluru 2020-2025, OpenCity.in CKAN API)
- Phase 3: Waste rankings + Census demographics + GIS boundaries

### 4. Repository Structure (DONE)
```
SwachhPulse/
|-- SwachhPulse.md
|-- scrapper.md
|-- till_now.md
|-- backend/                (empty)
|-- frontend/               (empty)
|-- models/                 (empty)
|-- notebook/               (empty)
|-- webreaper/
|   |-- webreaper/          (Python package)
|   |-- collect_phase2.py   (BBMP download script)
|   |-- collect_phase3.py   (Waste/Census/GIS script)
|   |-- requirements.txt
|-- data/
    |-- README.md
    |-- raw/
    |   |-- municipal/      (6 BBMP grievance CSVs, 105 MB)
    |   |-- waste/          (2 Swachh Survekshan CSVs)
    |   |-- weather/        (6 city weather CSVs)
    |   |-- demographics/   (Census 2011 districts CSV)
    |   |-- gis/            (India states GeoJSON)
    |   |-- sanitation/     (empty)
    |   |-- other/          (empty)
    |-- synthetic/
    |   |-- README.md
    |-- manifests/
        |-- datasets.json   (16 entries, full provenance)
```

---

## What Has NOT Been Started Yet

### Backend (Step 1-3 in dev order)
- [ ] PostgreSQL/PostGIS database schema
- [ ] SQLAlchemy models
- [ ] FastAPI application setup
- [ ] Citizen report API endpoints

### Frontend (Step 4)
- [ ] Citizen report submission form
- [ ] AI classification correction UI

### Machine Learning (Step 7)
- [ ] Feature engineering pipeline (merge BBMP complaints + weather + census)
- [ ] Hotspot risk model training
- [ ] Model evaluation

### Dashboard (Step 8)
- [ ] Risk visualization map
- [ ] Sanitation index display

### AI/GenAI (Step 9)
- [ ] LLM-based report extraction

### Deployment (Step 12-13)
- [ ] Docker setup
- [ ] CI/CD

---

## Next Steps (Recommended)

1. **Explore BBMP data** -- Profile the grievance categories, filter for sanitation/waste complaints
2. **Feature engineering** -- Merge complaints + weather by date, compute ward-level daily incident counts
3. **Database schema** -- Design PostgreSQL/PostGIS tables for incidents
4. **Baseline ML** -- Train hotspot prediction model on Bengaluru data
5. **Dashboard** -- Map visualization with ward-level risk
