"""SHA-256 checksum utilities for duplicate detection."""

import hashlib
from pathlib import Path


def compute_sha256(filepath: Path, chunk_size: int = 8192) -> str:
    """Compute SHA-256 hash of a file using chunked reading."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()
