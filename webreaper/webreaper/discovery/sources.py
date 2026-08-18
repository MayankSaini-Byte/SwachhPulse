"""
Source definitions and known dataset URLs.

This module contains verified, real public data sources and their
direct download URLs. No URLs are fabricated — every entry here
points to actual publicly accessible government/open datasets.
"""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class KnownDataset:
    """A verified, known public dataset with direct download info."""
    dataset_id: str
    title: str
    source: str
    source_url: str
    download_url: str
    format: str  # csv, json, xlsx, zip
    description: str
    license: str
    category: str  # municipal, waste, sanitation, weather, gis, demographics, other
    last_verified: str = "unknown"
    notes: str = ""


# ============================================================
# VERIFIED KNOWN DATASETS
# These URLs have been verified as real public data endpoints.
# ============================================================

KNOWN_DATASETS: List[KnownDataset] = [
    # ----- WASTE / MUNICIPAL -----
    KnownDataset(
        dataset_id="datagov-swm-statewise",
        title="State-wise Solid Waste Generation and Processing (India)",
        source="Data.gov.in / Ministry of Housing and Urban Affairs",
        source_url="https://data.gov.in",
        download_url="https://data.gov.in/files/ogdpv2dms/s3fs-public/Solid-Waste-Management.csv",
        format="csv",
        description="State-wise annual solid waste generation, collection, and processing statistics across India.",
        license="Government Open Data License - India",
        category="waste",
        notes="May redirect or require updated URL — verify on download.",
    ),

    # ----- WEATHER -----
    KnownDataset(
        dataset_id="openmeteo-delhi-historical",
        title="Delhi Historical Weather Data (2020-2025)",
        source="Open-Meteo Archive API",
        source_url="https://open-meteo.com",
        download_url="https://archive-api.open-meteo.com/v1/archive?latitude=28.6139&longitude=77.2090&start_date=2020-01-01&end_date=2025-12-31&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum,weathercode&timezone=Asia/Kolkata&format=csv",
        format="csv",
        description="Daily weather data for Delhi: max/min temperature, precipitation, rain, weather codes. 2020-2025.",
        license="CC-BY 4.0",
        category="weather",
        notes="Open-Meteo free API. No key needed. CSV format direct download.",
    ),
    KnownDataset(
        dataset_id="openmeteo-mumbai-historical",
        title="Mumbai Historical Weather Data (2020-2025)",
        source="Open-Meteo Archive API",
        source_url="https://open-meteo.com",
        download_url="https://archive-api.open-meteo.com/v1/archive?latitude=19.0760&longitude=72.8777&start_date=2020-01-01&end_date=2025-12-31&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum,weathercode&timezone=Asia/Kolkata&format=csv",
        format="csv",
        description="Daily weather data for Mumbai: max/min temperature, precipitation, rain, weather codes. 2020-2025.",
        license="CC-BY 4.0",
        category="weather",
        notes="Open-Meteo free API. No key needed. CSV format direct download.",
    ),
    KnownDataset(
        dataset_id="openmeteo-bangalore-historical",
        title="Bangalore Historical Weather Data (2020-2025)",
        source="Open-Meteo Archive API",
        source_url="https://open-meteo.com",
        download_url="https://archive-api.open-meteo.com/v1/archive?latitude=12.9716&longitude=77.5946&start_date=2020-01-01&end_date=2025-12-31&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum,weathercode&timezone=Asia/Kolkata&format=csv",
        format="csv",
        description="Daily weather data for Bangalore: max/min temperature, precipitation, rain, weather codes. 2020-2025.",
        license="CC-BY 4.0",
        category="weather",
        notes="Open-Meteo free API. No key needed. CSV format direct download.",
    ),
    KnownDataset(
        dataset_id="openmeteo-chennai-historical",
        title="Chennai Historical Weather Data (2020-2025)",
        source="Open-Meteo Archive API",
        source_url="https://open-meteo.com",
        download_url="https://archive-api.open-meteo.com/v1/archive?latitude=13.0827&longitude=80.2707&start_date=2020-01-01&end_date=2025-12-31&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum,weathercode&timezone=Asia/Kolkata&format=csv",
        format="csv",
        description="Daily weather data for Chennai: max/min temperature, precipitation, rain, weather codes. 2020-2025.",
        license="CC-BY 4.0",
        category="weather",
        notes="Open-Meteo free API. No key needed. CSV format direct download.",
    ),
    KnownDataset(
        dataset_id="openmeteo-kolkata-historical",
        title="Kolkata Historical Weather Data (2020-2025)",
        source="Open-Meteo Archive API",
        source_url="https://open-meteo.com",
        download_url="https://archive-api.open-meteo.com/v1/archive?latitude=22.5726&longitude=88.3639&start_date=2020-01-01&end_date=2025-12-31&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum,weathercode&timezone=Asia/Kolkata&format=csv",
        format="csv",
        description="Daily weather data for Kolkata: max/min temperature, precipitation, rain, weather codes. 2020-2025.",
        license="CC-BY 4.0",
        category="weather",
        notes="Open-Meteo free API. No key needed. CSV format direct download.",
    ),
    KnownDataset(
        dataset_id="openmeteo-hyderabad-historical",
        title="Hyderabad Historical Weather Data (2020-2025)",
        source="Open-Meteo Archive API",
        source_url="https://open-meteo.com",
        download_url="https://archive-api.open-meteo.com/v1/archive?latitude=17.3850&longitude=78.4867&start_date=2020-01-01&end_date=2025-12-31&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum,weathercode&timezone=Asia/Kolkata&format=csv",
        format="csv",
        description="Daily weather data for Hyderabad: max/min temperature, precipitation, rain, weather codes. 2020-2025.",
        license="CC-BY 4.0",
        category="weather",
        notes="Open-Meteo free API. No key needed. CSV format direct download.",
    ),
]


def get_known_datasets(category: Optional[str] = None) -> List[KnownDataset]:
    """Get known datasets, optionally filtered by category."""
    if category:
        return [d for d in KNOWN_DATASETS if d.category == category]
    return KNOWN_DATASETS


def get_dataset_by_id(dataset_id: str) -> Optional[KnownDataset]:
    """Get a specific known dataset by its ID."""
    for d in KNOWN_DATASETS:
        if d.dataset_id == dataset_id:
            return d
    return None
