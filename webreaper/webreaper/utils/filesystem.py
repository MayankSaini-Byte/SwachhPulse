"""Filesystem utilities — safe path handling, filename sanitization."""

import re
import unicodedata
from pathlib import Path
from datetime import datetime


def sanitize_filename(name: str) -> str:
    """
    Sanitize a filename to prevent path traversal and invalid characters.
    
    Removes:
    - Path separators (/, \\)
    - Null bytes
    - Control characters
    - Leading dots (hidden files)
    - Windows reserved names
    """
    # Normalize unicode
    name = unicodedata.normalize("NFKD", name)
    # Remove path separators and null bytes
    name = name.replace("/", "_").replace("\\", "_").replace("\x00", "")
    # Remove control characters
    name = re.sub(r"[\x00-\x1f\x7f]", "", name)
    # Remove Windows invalid chars
    name = re.sub(r'[<>:"|?*]', "_", name)
    # Remove leading dots
    name = name.lstrip(".")
    # Collapse multiple underscores/spaces
    name = re.sub(r"[_\s]+", "_", name)
    # Trim length
    name = name[:200]
    # Fallback
    if not name:
        name = "unnamed_file"
    return name


def safe_join(base: Path, *parts: str) -> Path:
    """
    Safely join path components, preventing path traversal.
    Raises ValueError if the result escapes base.
    """
    result = base
    for part in parts:
        part = sanitize_filename(part)
        result = result / part
    resolved = result.resolve()
    base_resolved = base.resolve()
    if not str(resolved).startswith(str(base_resolved)):
        raise ValueError(f"Path traversal detected: {resolved} escapes {base_resolved}")
    return resolved


def versioned_path(filepath: Path) -> Path:
    """
    If filepath exists, return a date-versioned alternative.
    Example: dataset.csv → dataset_2026-08-18.csv
    """
    if not filepath.exists():
        return filepath
    stem = filepath.stem
    suffix = filepath.suffix
    date_str = datetime.now().strftime("%Y-%m-%d")
    new_name = f"{stem}_{date_str}{suffix}"
    new_path = filepath.parent / new_name
    # If that also exists, add counter
    counter = 1
    while new_path.exists():
        new_name = f"{stem}_{date_str}_{counter}{suffix}"
        new_path = filepath.parent / new_name
        counter += 1
    return new_path


def ensure_dir(path: Path) -> Path:
    """Create directory and parents if they don't exist."""
    path.mkdir(parents=True, exist_ok=True)
    return path
