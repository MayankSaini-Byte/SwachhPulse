"""
Discovery / search engine — finds relevant datasets from configured sources.

Searches data.gov.in CKAN API and known dataset registries.
"""

import logging
import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict

import requests

from webreaper.config import get_settings, get_sources
from webreaper.discovery.sources import get_known_datasets, KNOWN_DATASETS, KnownDataset

logger = logging.getLogger("webreaper.discovery")


@dataclass
class DatasetResult:
    """A discovered dataset candidate."""
    title: str
    source: str
    url: str
    download_url: Optional[str]
    format: str
    description: str
    license: str
    last_updated: Optional[str]
    size: Optional[str]
    relevance_score: float
    category: str
    dataset_id: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


def search_known(query: str) -> List[DatasetResult]:
    """Search the known/verified dataset registry for matches."""
    query_lower = query.lower()
    terms = query_lower.split()
    results = []

    for ds in KNOWN_DATASETS:
        searchable = f"{ds.title} {ds.description} {ds.category} {ds.notes}".lower()
        # Score: count how many query terms match
        matches = sum(1 for t in terms if t in searchable)
        if matches > 0:
            score = matches / len(terms)
            results.append(DatasetResult(
                title=ds.title,
                source=ds.source,
                url=ds.source_url,
                download_url=ds.download_url,
                format=ds.format,
                description=ds.description,
                license=ds.license,
                last_updated=ds.last_verified,
                size=None,
                relevance_score=round(score, 2),
                category=ds.category,
                dataset_id=ds.dataset_id,
            ))

    results.sort(key=lambda r: r.relevance_score, reverse=True)
    return results


def search_ckan(query: str, base_url: str = "https://data.gov.in/api/3/action",
                rows: int = 10) -> List[DatasetResult]:
    """
    Search data.gov.in CKAN API for datasets.
    
    Note: data.gov.in CKAN API may have access restrictions.
    This function handles failures gracefully.
    """
    settings = get_settings()
    results = []

    try:
        url = f"{base_url}/package_search"
        params = {"q": query, "rows": rows}
        headers = {"User-Agent": settings.user_agent}

        logger.info(f"[DISCOVERY] Searching CKAN: {query}")
        resp = requests.get(url, params=params, headers=headers, timeout=settings.timeout)

        if resp.status_code != 200:
            logger.warning(f"[DISCOVERY] CKAN API returned {resp.status_code} — may require API key")
            return results

        data = resp.json()
        if not data.get("success"):
            logger.warning("[DISCOVERY] CKAN API returned success=false")
            return results

        for pkg in data.get("result", {}).get("results", []):
            # Extract resources (downloadable files)
            resources = pkg.get("resources", [])
            for res in resources:
                fmt = (res.get("format") or "").lower()
                if fmt in ("csv", "json", "xlsx", "xls", "zip"):
                    results.append(DatasetResult(
                        title=pkg.get("title", "Unknown"),
                        source="Data.gov.in",
                        url=pkg.get("url", ""),
                        download_url=res.get("url"),
                        format=fmt,
                        description=pkg.get("notes", "")[:300],
                        license=pkg.get("license_title", "Government of India"),
                        last_updated=pkg.get("metadata_modified"),
                        size=res.get("size"),
                        relevance_score=0.5,  # CKAN doesn't provide relevance scores
                        category=_guess_category(pkg.get("title", "") + " " + pkg.get("notes", "")),
                        dataset_id=pkg.get("id"),
                    ))

    except requests.exceptions.ConnectionError:
        logger.warning("[DISCOVERY] Cannot connect to CKAN API")
    except requests.exceptions.Timeout:
        logger.warning("[DISCOVERY] CKAN API timeout")
    except Exception as e:
        logger.warning(f"[DISCOVERY] CKAN search error: {e}")

    return results


def _guess_category(text: str) -> str:
    """Guess dataset category from text content."""
    text = text.lower()
    category_keywords = {
        "municipal": ["municipal", "corporation", "ward", "civic", "urban local"],
        "waste": ["waste", "garbage", "solid waste", "swm", "dump", "landfill", "refuse"],
        "sanitation": ["sanitation", "toilet", "sewage", "drainage", "open defecation", "swachh"],
        "weather": ["weather", "rainfall", "temperature", "precipitation", "climate", "meteorolog"],
        "gis": ["boundary", "shapefile", "geojson", "geospatial", "gis", "map", "coordinate"],
        "demographics": ["population", "census", "household", "demographic", "district"],
    }
    for cat, keywords in category_keywords.items():
        if any(kw in text for kw in keywords):
            return cat
    return "other"


def search(query: str, include_ckan: bool = True) -> List[DatasetResult]:
    """
    Master search function. Searches:
    1. Known/verified datasets
    2. CKAN API (data.gov.in) if enabled
    
    Deduplicates and ranks results.
    """
    logger.info(f"[DISCOVERY] Searching: {query}")

    # Search known datasets first (always reliable)
    results = search_known(query)
    logger.info(f"[DISCOVERY] Found {len(results)} known datasets")

    # Search CKAN if enabled
    if include_ckan:
        time.sleep(1)  # polite delay
        ckan_results = search_ckan(query)
        logger.info(f"[DISCOVERY] Found {len(ckan_results)} CKAN datasets")
        results.extend(ckan_results)

    # Deduplicate by download URL
    seen_urls = set()
    unique = []
    for r in results:
        key = r.download_url or r.url
        if key not in seen_urls:
            seen_urls.add(key)
            unique.append(r)

    # Sort by relevance
    unique.sort(key=lambda r: r.relevance_score, reverse=True)
    logger.info(f"[DISCOVERY] Total unique results: {len(unique)}")
    return unique
