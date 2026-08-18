You are working inside my existing SwachhPulse_Current project repository.

IMPORTANT:
Before writing code, inspect the repository structure and read the existing project markdown/documentation files, especially:

- SwachhPulse_Current.md
- README.md if present
- any existing docs/ or data-related files

Do NOT redesign the existing SwachhPulse application.
Do NOT modify the ML pipeline, backend, database, frontend, or existing project architecture unless absolutely required for the collector.

==================================================
PROJECT: WEBREAPER
==================================================

Build a standalone data-collection utility called:

WebReaper

Purpose:
WebReaper is ONLY a public-data discovery and collection layer for SwachhPulse.

Its responsibility is:

PUBLIC DATA SOURCE
      ↓
DISCOVER
      ↓
IDENTIFY DATASET
      ↓
DOWNLOAD
      ↓
VALIDATE BASIC FILE
      ↓
SAVE RAW DATA
      ↓
data/

It must NOT:

- train ML models
- clean datasets
- transform datasets
- perform feature engineering
- insert into PostgreSQL
- perform analytics
- generate predictions
- call the SwachhPulse ML pipeline
- overwrite existing raw datasets silently

Think of WebReaper as a "data vacuum" / ingestion collector.

==================================================
PRIMARY OUTPUT
==================================================

All downloaded datasets must ultimately be stored inside:

data/

Prefer a structure such as:

data/
├── raw/
│   ├── municipal/
│   ├── waste/
│   ├── sanitation/
│   ├── weather/
│   ├── gis/
│   ├── demographics/
│   └── other/
│
├── manifests/
│
└── README.md

If the existing project already has a data/ structure, inspect it first and adapt rather than destroying it.

RAW DATA MUST REMAIN RAW.

Never silently modify a downloaded CSV.

==================================================
CORE FUNCTION
==================================================

WebReaper should be able to discover useful PUBLIC datasets relevant to SwachhPulse.

Priority domains:

1. Municipal solid waste
2. Sanitation
3. Garbage collection
4. Waste generation
5. Waste processing
6. Municipal complaints/grievances
7. Collection vehicles/GPS
8. Ward-level municipal statistics
9. Population/demographics
10. Weather/rainfall
11. GIS/ward boundaries
12. Urban infrastructure
13. Environmental data

India should be the primary target.

Prioritize:

- Government of India open-data sources
- State government open-data portals
- Municipal corporation datasets
- public APIs
- official downloadable CSV/JSON datasets
- other legally/publicly accessible datasets

==================================================
DISCOVERY ENGINE
==================================================

Build a dataset discovery component.

It should accept queries such as:

    "municipal solid waste India"
    "garbage collection ward India"
    "sanitation complaints"
    "municipal waste generation"
    "ward population"
    "rainfall India"

The discovery engine should search configured public sources and identify candidate datasets.

Each discovered dataset should produce metadata such as:

    {
        "title": "...",
        "source": "...",
        "url": "...",
        "format": "CSV",
        "description": "...",
        "license": "...",
        "last_updated": "...",
        "size": "...",
        "relevance_score": 0.87
    }

DO NOT fabricate metadata.

If metadata cannot be determined, use null/unknown rather than inventing it.

==================================================
SOURCE PRIORITY
==================================================

Create a source registry/configuration.

Example conceptual structure:

sources/
    data_portals
    government
    municipal
    weather
    gis

The first implementation should prioritize official/public sources.

For every source, record:

- source name
- base URL
- discovery method
- whether API exists
- whether direct download exists
- supported formats
- notes
- terms/license if known

==================================================
DOWNLOAD ENGINE
==================================================

The downloader should support at minimum:

- CSV
- ZIP containing CSV
- JSON
- XLSX if practical

Primary target is CSV.

For a ZIP:

    download ZIP
        ↓
    extract safely
        ↓
    identify CSV files
        ↓
    copy RAW CSVs to data/raw/<category>/

Do not execute downloaded files.

Protect against:

- path traversal
- suspicious filenames
- unexpected file types
- huge downloads
- corrupted downloads

==================================================
CSV DOWNLOADER
==================================================

Create a reliable CSV downloader.

Requirements:

1. Stream large files instead of loading the entire file into memory.
2. Show download progress where practical.
3. Follow redirects.
4. Set reasonable timeouts.
5. Retry temporary failures.
6. Verify HTTP status.
7. Verify downloaded file is not empty.
8. Detect obvious HTML/error-page downloads pretending to be CSV.
9. Preserve the original file whenever possible.
10. Avoid overwriting an existing file by default.

Example:

    python -m webreaper download <dataset-url>

Expected result:

    data/raw/municipal/example_dataset.csv

==================================================
DUPLICATE HANDLING
==================================================

Never blindly overwrite existing data.

Calculate a checksum such as SHA-256.

Store:

    filename
    source_url
    download_timestamp
    sha256
    file_size
    dataset_title
    source
    category

If the exact file already exists:

    "Already downloaded — skipping."

If the URL points to updated content:

    save a new version rather than destroying the old raw file.

Example:

    example_dataset_2026-08-18.csv

or use a version directory.

==================================================
MANIFEST
==================================================

Every successful download must update a manifest:

data/manifests/datasets.json

Example:

{
    "dataset_id": "...",
    "title": "...",
    "source": "...",
    "source_url": "...",
    "downloaded_at": "...",
    "local_path": "...",
    "format": "csv",
    "size_bytes": 123456,
    "sha256": "...",
    "license": "...",
    "description": "...",
    "status": "downloaded"
}

This manifest is extremely important.

It creates provenance for every dataset.

==================================================
BASIC VALIDATION ONLY
==================================================

WebReaper may perform ONLY basic integrity checks.

Allowed:

- file exists
- file is not empty
- CSV can be opened
- detect delimiter
- detect encoding
- count columns
- count rows
- identify obvious malformed downloads

NOT allowed:

- removing nulls
- changing column names
- changing datatypes
- dropping duplicates
- normalization
- feature engineering
- imputation
- cleaning

The output must remain RAW.

If validation information is useful, put it in metadata, not into the raw CSV.

==================================================
CLI
==================================================

Create a clean CLI.

Examples:

    webreaper search "municipal solid waste India"

    webreaper search "sanitation complaints"

    webreaper inspect <dataset-url>

    webreaper download <dataset-url>

    webreaper download --query "municipal solid waste India"

    webreaper list

    webreaper manifest

    webreaper verify

Potential commands:

    search
    inspect
    download
    list
    manifest
    verify

==================================================
CONFIGURATION
==================================================

Use a configuration file rather than hardcoding everything.

Example:

config/

    sources.yaml
    settings.yaml

Settings could include:

- download directory
- timeout
- retry count
- max file size
- allowed extensions
- user agent
- whether overwrite is allowed

==================================================
LOGGING
==================================================

Use structured logging.

Example:

    [DISCOVERY]
    Searching: municipal solid waste India

    [FOUND]
    Dataset: Solid Waste Management Statistics

    [DOWNLOAD]
    URL: ...

    [VALIDATE]
    Format: CSV
    Rows: ...
    Columns: ...

    [SAVE]
    data/raw/waste/...

    [MANIFEST]
    Updated

Errors should be clear and actionable.

==================================================
PROJECT STRUCTURE
==================================================

Prefer something close to:

webreaper/
├── webreaper/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── discovery/
│   │   ├── __init__.py
│   │   ├── search.py
│   │   └── sources.py
│   ├── downloader/
│   │   ├── __init__.py
│   │   ├── http.py
│   │   ├── csv.py
│   │   └── archive.py
│   ├── validation/
│   │   ├── __init__.py
│   │   └── integrity.py
│   ├── metadata/
│   │   ├── __init__.py
│   │   └── manifest.py
│   └── utils/
│       ├── hashing.py
│       └── filesystem.py
│
├── config/
├── tests/
├── data/
│   ├── raw/
│   ├── manifests/
│   └── README.md
│
├── requirements.txt
└── README.md

Adapt this if the existing SwachhPulse repository has a better structure.

==================================================
IMPORTANT: DISCOVERY VS DOWNLOADING
==================================================

Do not assume that every search result has a direct CSV URL.

For each candidate:

    Search result
        ↓
    Dataset page
        ↓
    Identify official download/API endpoint
        ↓
    Inspect
        ↓
    Download

If a dataset is only available through an API, implement API downloading separately.

==================================================
API SUPPORT
==================================================

Support public JSON APIs where practical.

Pipeline:

    API
     ↓
    Raw JSON
     ↓
    data/raw/
    
Do NOT automatically convert API data into cleaned CSV.

If conversion to CSV is implemented as an optional feature, preserve the original raw JSON too.

==================================================
ROBOTS / TERMS / ACCESS
==================================================

This is a legitimate public-data collector.

Do NOT bypass:

- authentication
- paywalls
- CAPTCHAs
- access controls
- anti-bot protections
- rate limits
- robots restrictions where applicable

Prefer official APIs and direct public downloads.

Implement polite request behavior:

- rate limiting
- retries with backoff
- descriptive User-Agent
- caching where appropriate

==================================================
AI / LLM USAGE
==================================================

Do NOT make an LLM mandatory for downloading.

The core downloader must work without an LLM.

An optional AI discovery layer may:

    user query
        ↓
    query expansion
        ↓
    dataset ranking
        ↓
    human confirmation
        ↓
    downloader

But never allow an LLM to invent a download URL.

URLs must come from actual discovered pages/API responses.

==================================================
SWACHPULSE INTEGRATION
==================================================

WebReaper should remain loosely coupled to SwachhPulse.

The only guaranteed integration is:

    WebReaper
        ↓
    data/raw/
        ↓
    SwachhPulse data pipeline

Do NOT import SwachhPulse ML code into WebReaper.

Do NOT call the database from WebReaper.

Do NOT train anything.

Think:

    WebReaper = Collector

    SwachhPulse = Consumer

==================================================
README
==================================================

Write a clear README explaining:

1. What WebReaper is.
2. What it does.
3. What it deliberately does NOT do.
4. Supported sources.
5. CLI usage.
6. Folder structure.
7. Dataset provenance.
8. Safety/legal constraints.
9. How SwachhPulse consumes the raw data.

Include an example end-to-end run.

==================================================
TESTING
==================================================

Write tests for:

- URL handling
- filename sanitization
- checksum calculation
- duplicate detection
- CSV validation
- ZIP extraction
- path traversal prevention
- manifest generation
- retry behavior
- corrupted download handling

Use mock HTTP responses for tests.

Tests must not depend on live external websites.

==================================================
IMPLEMENTATION RULE
==================================================

FIRST:

1. Inspect the existing repository.
2. Read SwachhPulse_Current.md.
3. Identify existing data folders and code.
4. Do not duplicate existing functionality.
5. Propose the exact WebReaper structure.
6. Then implement it.

Do not rewrite the entire project.

Do not create fake datasets.

Do not hardcode fake download URLs.

Do not claim that a source supports CSV/API access unless it has actually been verified.

The final result should be a clean, independently runnable collector that can discover and download legitimate public datasets and dump the untouched raw files into the SwachhPulse data directory.