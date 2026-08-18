"""
HTTP download engine — streaming downloads with retry, progress, and safety.
"""

import logging
import time
from pathlib import Path
from typing import Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from webreaper.config import get_settings

logger = logging.getLogger("webreaper.downloader")


def create_session() -> requests.Session:
    """Create a requests session with retry strategy and proper headers."""
    settings = get_settings()
    session = requests.Session()

    # Retry strategy with exponential backoff
    retry = Retry(
        total=settings.retry_count,
        backoff_factor=settings.retry_backoff,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    session.headers.update({
        "User-Agent": settings.user_agent,
        "Accept": "text/csv,application/json,application/octet-stream,*/*",
    })

    return session


def stream_download(url: str, dest: Path, session: Optional[requests.Session] = None) -> Tuple[bool, str]:
    """
    Stream-download a file from URL to dest path.
    
    Returns:
        (success: bool, message: str)
    """
    settings = get_settings()
    if session is None:
        session = create_session()

    try:
        logger.info(f"[DOWNLOAD] Starting: {url}")
        logger.info(f"[DOWNLOAD] Destination: {dest}")

        # HEAD request first to check size
        try:
            head = session.head(url, timeout=settings.timeout, allow_redirects=True)
            content_length = int(head.headers.get("Content-Length", 0))
            if content_length > settings.max_file_size:
                return False, f"File too large: {content_length} bytes (max {settings.max_file_size})"
        except Exception:
            content_length = 0  # Unknown size, proceed anyway

        # Stream GET
        resp = session.get(url, stream=True, timeout=settings.timeout, allow_redirects=True)
        resp.raise_for_status()

        # Check content type for HTML masquerading as data
        content_type = resp.headers.get("Content-Type", "").lower()
        if "text/html" in content_type and not url.endswith(".html"):
            # Read first chunk to verify
            first_chunk = next(resp.iter_content(chunk_size=1024), b"")
            if b"<!DOCTYPE" in first_chunk or b"<html" in first_chunk:
                return False, "Download returned HTML page instead of data file"
            # If not HTML, we keep this chunk
            initial_chunk = first_chunk
        else:
            initial_chunk = None

        # Ensure parent directory exists
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Stream to file
        downloaded = 0
        with open(dest, "wb") as f:
            if initial_chunk:
                f.write(initial_chunk)
                downloaded += len(initial_chunk)

            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    # Safety: check max size during download
                    if downloaded > settings.max_file_size:
                        f.close()
                        dest.unlink(missing_ok=True)
                        return False, f"Download exceeded max file size ({settings.max_file_size} bytes)"

        # Verify not empty
        if downloaded == 0:
            dest.unlink(missing_ok=True)
            return False, "Downloaded file is empty (0 bytes)"

        logger.info(f"[DOWNLOAD] Complete: {downloaded} bytes → {dest}")
        return True, f"Downloaded {downloaded} bytes"

    except requests.exceptions.HTTPError as e:
        return False, f"HTTP error: {e}"
    except requests.exceptions.ConnectionError:
        return False, "Connection error — could not reach server"
    except requests.exceptions.Timeout:
        return False, f"Timeout after {settings.timeout}s"
    except Exception as e:
        return False, f"Download error: {e}"


def inspect_url(url: str, session: Optional[requests.Session] = None) -> dict:
    """
    Inspect a URL without downloading — HEAD request for metadata.
    """
    settings = get_settings()
    if session is None:
        session = create_session()

    try:
        resp = session.head(url, timeout=settings.timeout, allow_redirects=True)
        return {
            "url": url,
            "final_url": resp.url,
            "status_code": resp.status_code,
            "content_type": resp.headers.get("Content-Type", "unknown"),
            "content_length": resp.headers.get("Content-Length", "unknown"),
            "last_modified": resp.headers.get("Last-Modified", "unknown"),
            "server": resp.headers.get("Server", "unknown"),
            "redirected": resp.url != url,
        }
    except Exception as e:
        return {
            "url": url,
            "error": str(e),
            "status_code": None,
        }
