"""
WebReaper CLI — command-line interface for dataset discovery and collection.

Usage:
    python -m webreaper search "municipal solid waste India"
    python -m webreaper download --all
    python -m webreaper download --category weather
    python -m webreaper download --id openmeteo-delhi-historical
    python -m webreaper inspect <url>
    python -m webreaper list
    python -m webreaper manifest
    python -m webreaper verify
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path

from webreaper.config import get_settings, get_sources
from webreaper.discovery.search import search, search_known
from webreaper.discovery.sources import get_known_datasets, get_dataset_by_id, KNOWN_DATASETS
from webreaper.downloader.http import stream_download, inspect_url, create_session
from webreaper.validation.integrity import validate_file
from webreaper.metadata.manifest import ManifestManager
from webreaper.utils.filesystem import sanitize_filename, versioned_path, ensure_dir
from webreaper.utils.hashing import compute_sha256

# ---- Logging Setup ----
import io

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("webreaper")


def cmd_search(args):
    """Search for datasets matching a query."""
    query = " ".join(args.query)
    print(f"\n{'='*60}")
    print(f"  [DISCOVERY] Searching: {query}")
    print(f"{'='*60}\n")

    results = search(query, include_ckan=not args.no_ckan)

    if not results:
        print("  No datasets found.\n")
        return

    for i, r in enumerate(results, 1):
        print(f"  [{i}] {r.title}")
        print(f"      Source:    {r.source}")
        print(f"      Format:   {r.format.upper()}")
        print(f"      Category: {r.category}")
        print(f"      Score:    {r.relevance_score}")
        if r.download_url:
            print(f"      URL:      {r.download_url[:80]}...")
        print(f"      {r.description[:120]}")
        print()

    print(f"  Found {len(results)} dataset(s).\n")


def cmd_download(args):
    """Download datasets."""
    settings = get_settings()
    manifest = ManifestManager()
    session = create_session()

    datasets_to_download = []

    if args.url:
        # Direct URL download
        _download_url(args.url, args.category or "other", settings, manifest, session)
        return

    if args.id:
        # Download specific known dataset
        ds = get_dataset_by_id(args.id)
        if not ds:
            print(f"  [ERROR] Unknown dataset ID: {args.id}")
            print(f"  Available IDs: {', '.join(d.dataset_id for d in KNOWN_DATASETS)}")
            return
        datasets_to_download = [ds]

    elif args.category:
        # Download all known datasets in a category
        datasets_to_download = get_known_datasets(args.category)
        if not datasets_to_download:
            print(f"  [ERROR] No known datasets for category: {args.category}")
            return

    elif args.all:
        # Download ALL known datasets
        datasets_to_download = KNOWN_DATASETS

    elif args.query:
        # Search and download matches
        query = " ".join(args.query)
        results = search_known(query)
        for r in results:
            ds = get_dataset_by_id(r.dataset_id)
            if ds:
                datasets_to_download.append(ds)

    else:
        print("  [ERROR] Specify --url, --id, --category, --all, or --query")
        return

    if not datasets_to_download:
        print("  No datasets to download.")
        return

    print(f"\n{'='*60}")
    print(f"  [DOWNLOAD] {len(datasets_to_download)} dataset(s) queued")
    print(f"{'='*60}\n")

    success_count = 0
    fail_count = 0

    for ds in datasets_to_download:
        print(f"  +-- {ds.title}")
        print(f"  |   Source: {ds.source}")
        print(f"  |   URL: {ds.download_url[:70]}...")

        # Determine destination
        category_dir = ensure_dir(settings.raw_dir / ds.category)
        filename = sanitize_filename(f"{ds.dataset_id}.{ds.format}")
        dest = category_dir / filename

        # Check for existing file
        if dest.exists() and not settings.overwrite:
            existing_hash = compute_sha256(dest)
            existing_entry = manifest.find_by_sha256(existing_hash)
            if existing_entry:
                print(f"  |   [SKIP] Already downloaded -- skipping.")
                print(f"  +-- SHA256: {existing_hash[:16]}...\n")
                continue
            else:
                dest = versioned_path(dest)

        # Download
        ok, msg = stream_download(ds.download_url, dest, session)

        if ok:
            print(f"  |   [OK] {msg}")

            # Validate
            val = validate_file(dest)
            if val["validation_passed"]:
                print(f"  |   [OK] Validation passed", end="")
                if val.get("details", {}).get("num_rows") is not None:
                    print(f" -- {val['details']['num_rows']} rows, {val['details']['num_columns']} cols")
                else:
                    print()
            else:
                print(f"  |   [WARN] Validation: {val.get('errors', ['unknown'])}")

            # Add to manifest
            entry = manifest.add_entry(
                dataset_id=ds.dataset_id,
                title=ds.title,
                source=ds.source,
                source_url=ds.download_url,
                local_path=dest,
                format=ds.format,
                license=ds.license,
                description=ds.description,
                category=ds.category,
                validation_result=val,
            )
            print(f"  |   [OK] Manifest updated")
            print(f"  +-- Saved: {dest}\n")
            success_count += 1
        else:
            print(f"  |   [FAIL] FAILED: {msg}")
            print(f"  +--\n")
            fail_count += 1

        # Polite delay between downloads
        time.sleep(settings.request_delay)

    print(f"{'='*60}")
    print(f"  Done: {success_count} downloaded, {fail_count} failed")
    print(f"{'='*60}\n")


def _download_url(url: str, category: str, settings, manifest, session):
    """Download a single URL."""
    from urllib.parse import urlparse

    parsed = urlparse(url)
    filename = Path(parsed.path).name or "download"
    filename = sanitize_filename(filename)

    category_dir = ensure_dir(settings.raw_dir / category)
    dest = category_dir / filename

    if dest.exists() and not settings.overwrite:
        dest = versioned_path(dest)

    print(f"\n  [DOWNLOAD] {url}")
    ok, msg = stream_download(url, dest, session)

    if ok:
        print(f"  [OK] {msg}")
        val = validate_file(dest)
        fmt = dest.suffix.lstrip(".") or "unknown"
        manifest.add_entry(
            dataset_id=f"manual-{filename}",
            title=filename,
            source="Manual URL",
            source_url=url,
            local_path=dest,
            format=fmt,
            category=category,
            validation_result=val,
        )
        print(f"  [OK] Saved: {dest}\n")
    else:
        print(f"  [FAIL] FAILED: {msg}\n")


def cmd_inspect(args):
    """Inspect a URL without downloading."""
    url = args.url
    print(f"\n  [INSPECT] {url}\n")

    info = inspect_url(url)
    for k, v in info.items():
        print(f"    {k}: {v}")
    print()


def cmd_list(args):
    """List all known datasets."""
    datasets = KNOWN_DATASETS
    if args.category:
        datasets = get_known_datasets(args.category)

    print(f"\n{'='*60}")
    print(f"  [REGISTRY] Known Datasets")
    print(f"{'='*60}\n")

    categories = {}
    for ds in datasets:
        categories.setdefault(ds.category, []).append(ds)

    for cat, items in sorted(categories.items()):
        print(f"  -- {cat.upper()} ({len(items)}) --")
        for ds in items:
            print(f"    * {ds.dataset_id}")
            print(f"      {ds.title}")
            print(f"      {ds.source} | {ds.format.upper()}")
            print()

    print(f"  Total: {len(datasets)} datasets\n")


def cmd_manifest(args):
    """Show manifest summary."""
    manifest = ManifestManager()
    summary = manifest.summary()
    entries = manifest.get_all()

    print(f"\n{'='*60}")
    print(f"  [MANIFEST] Dataset Provenance")
    print(f"{'='*60}\n")

    print(f"  Total datasets: {summary['total_datasets']}")
    print(f"  Total size:     {summary['total_size_mb']} MB")
    print(f"  Categories:     {json.dumps(summary['categories'], indent=2)}")
    print()

    if entries:
        for e in entries:
            print(f"  - {e['title']}")
            print(f"    ID:       {e['dataset_id']}")
            print(f"    Source:   {e['source']}")
            print(f"    Path:     {e['local_path']}")
            print(f"    Size:     {e['size_bytes']} bytes")
            print(f"    SHA256:   {e['sha256'][:32]}...")
            print(f"    Date:     {e['downloaded_at']}")
            print(f"    Status:   {e['status']}")
            print()


def cmd_verify(args):
    """Verify integrity of all downloaded files."""
    manifest = ManifestManager()
    results = manifest.verify_all()

    print(f"\n{'='*60}")
    print(f"  [VERIFY] Integrity Check")
    print(f"{'='*60}\n")

    ok_count = 0
    fail_count = 0

    for r in results:
        status = "[OK]" if r["exists"] and r["checksum_match"] else "[FAIL]"
        if r["exists"] and r["checksum_match"]:
            ok_count += 1
        else:
            fail_count += 1

        print(f"  {status} {r['title']}")
        if not r["exists"]:
            print(f"    FILE MISSING: {r['path']}")
        elif not r["checksum_match"]:
            print(f"    CHECKSUM MISMATCH!")
            print(f"    Recorded: {r.get('recorded_sha256', 'N/A')[:32]}...")
            print(f"    Current:  {r.get('current_sha256', 'N/A')[:32]}...")
        print()

    print(f"  Results: {ok_count} OK, {fail_count} failed\n")


def cmd_sources(args):
    """List configured data sources."""
    sources = get_sources()

    print(f"\n{'='*60}")
    print(f"  [SOURCES] Configured Data Sources")
    print(f"{'='*60}\n")

    for s in sources:
        print(f"  * {s.name}")
        print(f"    URL:      {s.base_url}")
        print(f"    API:      {'Yes' if s.has_api else 'No'}")
        print(f"    Direct:   {'Yes' if s.has_direct_download else 'No'}")
        print(f"    Formats:  {', '.join(s.supported_formats)}")
        print(f"    License:  {s.license}")
        print(f"    Notes:    {s.notes}")
        print()


def main():
    parser = argparse.ArgumentParser(
        prog="webreaper",
        description="WebReaper — Public data collector for SwachhPulse",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # search
    p_search = subparsers.add_parser("search", help="Search for datasets")
    p_search.add_argument("query", nargs="+", help="Search query")
    p_search.add_argument("--no-ckan", action="store_true", help="Skip CKAN API search")
    p_search.set_defaults(func=cmd_search)

    # download
    p_download = subparsers.add_parser("download", help="Download datasets")
    p_download.add_argument("--url", help="Direct URL to download")
    p_download.add_argument("--id", help="Known dataset ID to download")
    p_download.add_argument("--category", help="Download all datasets in category")
    p_download.add_argument("--all", action="store_true", help="Download all known datasets")
    p_download.add_argument("--query", nargs="+", help="Search and download matches")
    p_download.set_defaults(func=cmd_download)

    # inspect
    p_inspect = subparsers.add_parser("inspect", help="Inspect a URL")
    p_inspect.add_argument("url", help="URL to inspect")
    p_inspect.set_defaults(func=cmd_inspect)

    # list
    p_list = subparsers.add_parser("list", help="List known datasets")
    p_list.add_argument("--category", help="Filter by category")
    p_list.set_defaults(func=cmd_list)

    # manifest
    p_manifest = subparsers.add_parser("manifest", help="Show manifest")
    p_manifest.set_defaults(func=cmd_manifest)

    # verify
    p_verify = subparsers.add_parser("verify", help="Verify file integrity")
    p_verify.set_defaults(func=cmd_verify)

    # sources
    p_sources = subparsers.add_parser("sources", help="List configured sources")
    p_sources.set_defaults(func=cmd_sources)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
