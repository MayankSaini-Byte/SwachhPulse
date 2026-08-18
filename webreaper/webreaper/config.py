"""
WebReaper configuration — loads settings and source registry.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Settings:
    """Global WebReaper settings."""
    # Paths
    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent)
    data_dir: Path = field(default=None)
    raw_dir: Path = field(default=None)
    manifest_dir: Path = field(default=None)

    # Download
    timeout: int = 60
    retry_count: int = 3
    retry_backoff: float = 2.0
    max_file_size: int = 500 * 1024 * 1024  # 500 MB
    allowed_extensions: tuple = (".csv", ".json", ".xlsx", ".xls", ".zip", ".geojson", ".shp")
    user_agent: str = "WebReaper/0.1 (SwachhPulse Student Project; data collection)"
    overwrite: bool = False

    # Rate limiting
    request_delay: float = 1.0  # seconds between requests

    def __post_init__(self):
        if self.data_dir is None:
            self.data_dir = self.project_root / "data"
        if self.raw_dir is None:
            self.raw_dir = self.data_dir / "raw"
        if self.manifest_dir is None:
            self.manifest_dir = self.data_dir / "manifests"


@dataclass
class SourceConfig:
    """Configuration for a single data source."""
    name: str
    base_url: str
    api_endpoint: Optional[str] = None
    discovery_method: str = "api"  # api, direct, scrape
    has_api: bool = False
    has_direct_download: bool = True
    supported_formats: tuple = ("csv",)
    notes: str = ""
    license: str = "unknown"
    category: str = "other"


# ----- Source Registry -----

SOURCES = [
    SourceConfig(
        name="Data.gov.in",
        base_url="https://data.gov.in",
        api_endpoint="https://data.gov.in/api/3/action",
        discovery_method="ckan_api",
        has_api=True,
        has_direct_download=True,
        supported_formats=("csv", "json", "xlsx", "xml"),
        notes="India Government Open Data Platform. CKAN-based API.",
        license="Government Open Data License - India",
        category="government",
    ),
    SourceConfig(
        name="Swachh Bharat Mission",
        base_url="https://sbm.gov.in",
        discovery_method="direct",
        has_api=False,
        has_direct_download=True,
        supported_formats=("csv", "xlsx"),
        notes="Swachh Bharat Mission official portal. Limited public datasets.",
        license="Government of India",
        category="sanitation",
    ),
    SourceConfig(
        name="CPCB Environmental Data",
        base_url="https://cpcb.nic.in",
        discovery_method="direct",
        has_api=False,
        has_direct_download=True,
        supported_formats=("csv", "xlsx", "pdf"),
        notes="Central Pollution Control Board. Waste and environmental data.",
        license="Government of India",
        category="waste",
    ),
    SourceConfig(
        name="Census India",
        base_url="https://censusindia.gov.in",
        discovery_method="direct",
        has_api=False,
        has_direct_download=True,
        supported_formats=("csv", "xlsx"),
        notes="Census of India. Population and demographic data.",
        license="Government of India",
        category="demographics",
    ),
    SourceConfig(
        name="Open Meteo Weather",
        base_url="https://open-meteo.com",
        api_endpoint="https://archive-api.open-meteo.com/v1/archive",
        discovery_method="api",
        has_api=True,
        has_direct_download=False,
        supported_formats=("json", "csv"),
        notes="Free weather API. Historical and forecast data. No API key needed.",
        license="CC-BY 4.0",
        category="weather",
    ),
    SourceConfig(
        name="OpenStreetMap / Overpass",
        base_url="https://overpass-api.de",
        api_endpoint="https://overpass-api.de/api/interpreter",
        discovery_method="api",
        has_api=True,
        has_direct_download=False,
        supported_formats=("json", "xml"),
        notes="OpenStreetMap data via Overpass API. GIS features.",
        license="ODbL",
        category="gis",
    ),
]


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


def get_sources() -> list:
    """Get all configured data sources."""
    return SOURCES


def get_source_by_name(name: str) -> Optional[SourceConfig]:
    """Find a source by name (case-insensitive)."""
    for src in SOURCES:
        if src.name.lower() == name.lower():
            return src
    return None
