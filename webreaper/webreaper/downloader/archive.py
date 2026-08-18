"""
Archive extraction — safe ZIP handling with path traversal protection.
"""

import logging
import zipfile
from pathlib import Path
from typing import List, Optional

from webreaper.utils.filesystem import sanitize_filename, safe_join

logger = logging.getLogger("webreaper.downloader.archive")

# Maximum extracted size to prevent zip bombs
MAX_EXTRACT_SIZE = 1_000_000_000  # 1 GB

# Dangerous file extensions
BLOCKED_EXTENSIONS = {".exe", ".bat", ".cmd", ".com", ".scr", ".pif", ".vbs", ".js", ".ps1"}


def extract_zip(zip_path: Path, dest_dir: Path) -> List[Path]:
    """
    Safely extract a ZIP file to dest_dir.
    
    Protections:
    - Path traversal prevention
    - Zip bomb detection (size limit)
    - Blocked file extension filtering
    - Suspicious filename filtering
    
    Returns list of extracted file paths.
    """
    extracted = []

    if not zipfile.is_zipfile(zip_path):
        logger.error(f"[ARCHIVE] Not a valid ZIP file: {zip_path}")
        return extracted

    with zipfile.ZipFile(zip_path, "r") as zf:
        # Check total uncompressed size
        total_size = sum(info.file_size for info in zf.infolist())
        if total_size > MAX_EXTRACT_SIZE:
            logger.error(f"[ARCHIVE] ZIP too large when extracted: {total_size} bytes")
            return extracted

        for info in zf.infolist():
            # Skip directories
            if info.is_dir():
                continue

            filename = Path(info.filename).name
            suffix = Path(filename).suffix.lower()

            # Block dangerous extensions
            if suffix in BLOCKED_EXTENSIONS:
                logger.warning(f"[ARCHIVE] Skipping blocked file: {filename}")
                continue

            # Sanitize filename
            safe_name = sanitize_filename(filename)

            # Build safe output path
            try:
                out_path = safe_join(dest_dir, safe_name)
            except ValueError as e:
                logger.warning(f"[ARCHIVE] Path traversal blocked: {e}")
                continue

            # Extract
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as source, open(out_path, "wb") as target:
                while True:
                    chunk = source.read(8192)
                    if not chunk:
                        break
                    target.write(chunk)

            extracted.append(out_path)
            logger.info(f"[ARCHIVE] Extracted: {safe_name}")

    logger.info(f"[ARCHIVE] Extracted {len(extracted)} files from {zip_path.name}")
    return extracted
