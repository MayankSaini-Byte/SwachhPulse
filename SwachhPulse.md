# SwachhPulse — Current Build Plan

## Purpose

SwachhPulse is currently a student-built civic-tech prototype for SIH1322 Domestic Waste Management.

The current version is intentionally constrained to the user's existing technical skill set rather than pretending to be a full government production platform.

## Current Project Goal

Build a working system that:

1. Accepts citizen sanitation reports.
2. Stores location/time/evidence.
3. Uses an LLM API for structured report understanding.
4. Uses municipal/open data + GIS/weather features for ML.
5. Predicts sanitation hotspot risk.
6. Shows risk and incidents on a dashboard.
7. Produces a sanitation score.
8. Demonstrates a basic municipality action workflow.

The core product loop is:

```text
Citizen Report
      ↓
FastAPI
      ↓
LLM / NLP
      ↓
Structured Incident
      ↓
PostgreSQL/PostGIS
      ↓
ML Risk Model
      ↓
Sanitation Index
      ↓
Dashboard
```

---

# 1. Current Scope

## A. Citizen reporting

Input:

- photo;
- text;
- location;
- timestamp.

Output:

```json
{
  "category": "open_dumping",
  "severity": "high",
  "location": "...",
  "confidence": 0.91
}
```

The citizen should be able to correct the AI classification before submission.

## B. Municipal/open data

Use available datasets for initial development.

Priority sources:

- Government Open Data Platform;
- municipal solid-waste datasets;
- ward/collection datasets;
- weather;
- OpenStreetMap/geospatial context.

The project must clearly separate:

```text
REAL DATA
SYNTHETIC DATA
DEMO DATA
```

Never claim synthetic/demo observations are real.

## C. Hotspot prediction

Initial target:

```text
Will a sanitation incident occur
in a ward/grid cell during the next 24–48 hours?
```

Start with:

- Logistic Regression;
- Random Forest;
- XGBoost/Gradient Boosting if useful.

Evaluate with:

- Precision;
- Recall;
- F1;
- PR-AUC;
- ROC-AUC;
- confusion matrix;
- calibration where possible.

## D. GIS

Use:

- PostgreSQL;
- PostGIS;
- OpenStreetMap/municipal spatial data.

Initial spatial features:

```text
incident count within radius
distance to road
distance to market
distance to park
distance to collection point
population/household context
```

## E. Sanitation Index

Create a transparent 0–100 score based on documented factors such as:

- incident density;
- unresolved incident burden;
- recurrence;
- resolution rate;
- collection reliability when data exists;
- predicted risk.

Do not let the LLM calculate the score.

---

# 2. Current Tech Stack

## Core

```text
Python
pandas
NumPy
scikit-learn
FastAPI
SQLAlchemy
PostgreSQL
PostGIS
Docker
Git/GitHub
HTML/CSS/JavaScript
```

## GenAI

Use a cloud LLM API only for language-heavy tasks:

- report extraction;
- classification support;
- complaint drafting;
- summaries.

Do not call the LLM for every request.

## Optional current tools

```text
Supabase
Hugging Face
```

Use them only where they simplify deployment.

---

# 3. Current AI Architecture

```text
User
 ↓
Basic validation
 ↓
FastAPI
 ↓
LLM for structured extraction
 ↓
Rule-based validation
 ↓
PostgreSQL/PostGIS
 ↓
ML model
 ↓
Dashboard
```

The LLM is not the source of truth for:

- numeric prediction;
- geospatial calculations;
- sanitation index;
- official complaint closure.

---

# 4. Current Data Sources

The project should not depend only on CCTV or community reports.

Preferred current sources:

### Primary operational data

- municipal complaints;
- door-to-door collection records;
- collection schedules;
- vehicle GPS if available;
- waste-weight/weighbridge data if available;
- bin/collection-point inventory;
- waste-processing records.

### Contextual data

- ward boundaries;
- population/households;
- OpenStreetMap;
- weather;
- festivals/events where available.

### Community/visual

- citizen reports;
- images/videos;
- CCTV only as an optional later module.

Because access to real municipal operational data may be limited, the MVP can use:

```text
public/open data
+
controlled demo data
+
small real pilot dataset
```

---

# 5. Current ML Priority

Do not build multiple complicated models initially.

### Model 1 — Hotspot risk

```text
historical incidents
+
time
+
location
+
weather
+
collection context
        ↓
risk probability
```

### Optional Model 2 — Waste-load forecast

Only after enough historical data exists.

---

# 6. Current AI/GenAI Features

The first useful GenAI workflow is:

```text
Citizen text/photo
       ↓
structured extraction
       ↓
category
severity
location clues
duration
       ↓
duplicate search
       ↓
municipal incident
```

Possible later addition:

RAG over municipal records to explain:

> Why is this ward currently high-risk?

Do not add RAG before the underlying records exist.

---

# 7. Current Duplicate Detection

At minimum:

```text
location proximity
+
timestamp proximity
+
text similarity
```

Later:

```text
image embeddings
+
multimodal similarity
```

If multiple reports appear to refer to the same event:

```text
Many reports
    ↓
One master incident
+
supporting observations
```

---

# 8. Current Development Order

```text
1. Database
2. FastAPI
3. Citizen report API
4. Frontend report form
5. Open-data ingestion
6. GIS/PostGIS
7. Baseline ML
8. Dashboard
9. GenAI extraction
10. Duplicate detection
11. Sanitation index
12. Docker deployment
13. Basic CI/CD
```

The system should be demonstrable before all advanced features are complete.

---

# 9. Current Repository Structure

```text
swachhpulse/
├── frontend/
├── backend/
├── ml/
│   ├── data/
│   ├── notebooks/
│   ├── training/
│   ├── inference/
│   └── models/
├── genai/
├── db/
├── scripts/
├── tests/
├── docs/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# 10. Current Limitations

This is a student prototype, not a production government deployment.

Known limitations:

- limited local labeled data;
- uncertain access to municipal GPS/weighbridge records;
- LLM API latency;
- cloud dependency for some AI features;
- limited CV capability;
- no true city-scale deployment;
- no validated government workflow integration;
- no large-scale monitoring;
- limited security hardening.

These limitations should be stated honestly.

---

# 11. Current Success Criteria

The current version is successful if the team can demonstrate:

```text
Citizen report
      ↓
AI structured extraction
      ↓
Incident stored with location
      ↓
Risk prediction
      ↓
Map/dashboard
      ↓
Municipal priority
```

A smaller system that works end-to-end is preferred over many incomplete features.

---

# 12. Current Future Direction

After the current MVP works, the project can evolve toward the 10/10 resume version documented separately.

The next major upgrades should be:

1. richer operational data;
2. stronger geospatial modelling;
3. time-series forecasting;
4. SHAP/XAI;
5. MLOps;
6. model monitoring/drift;
7. role-based access;
8. event-driven processing;
9. computer vision;
10. measurable pilot impact.
