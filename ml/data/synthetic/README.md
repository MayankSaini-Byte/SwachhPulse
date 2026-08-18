# Synthetic / Demo Data

All files in this directory are **synthetically generated** or **demo-only** data.

## Rules

- Every file MUST be clearly labeled as synthetic or demo
- NEVER present synthetic data as real data
- Use only for development, testing, and demonstration purposes
- Prefix filenames with `synthetic_` or `demo_` where possible

## Usage

These datasets are used during development when real municipal/government data
is unavailable. They allow the ML pipeline, dashboard, and APIs to be tested
end-to-end without waiting for real data access.

## Data Labeling

| Prefix        | Purpose                                    |
|---------------|--------------------------------------------|
| `synthetic_`  | Generated programmatically for ML training |
| `demo_`       | Hand-crafted samples for demonstrations    |
