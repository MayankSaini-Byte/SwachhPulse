"""
CSV-specific download logic — validates that downloaded files are actual CSV.
"""

import logging
import csv
import io
from pathlib import Path
from typing import Optional, Dict

logger = logging.getLogger("webreaper.downloader.csv")


def detect_csv_properties(filepath: Path) -> Dict:
    """
    Detect basic CSV properties without modifying the file.
    
    Returns metadata about the CSV (delimiter, encoding, rows, columns).
    This is VALIDATION ONLY — no cleaning or modification.
    """
    result = {
        "is_valid_csv": False,
        "delimiter": None,
        "encoding": None,
        "num_columns": None,
        "num_rows": None,
        "columns": None,
        "error": None,
    }

    # Try common encodings
    for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
        try:
            with open(filepath, "r", encoding=encoding, errors="strict") as f:
                # Read first few lines to detect
                sample = f.read(8192)
                if not sample.strip():
                    result["error"] = "File is empty or whitespace-only"
                    return result

                # Check for HTML content
                if sample.strip().startswith(("<!DOCTYPE", "<html", "<HTML", "<?xml")):
                    result["error"] = "File contains HTML/XML, not CSV"
                    return result

                # Detect delimiter
                try:
                    dialect = csv.Sniffer().sniff(sample)
                    result["delimiter"] = dialect.delimiter
                except csv.Error:
                    result["delimiter"] = ","  # default assumption

                # Reset and count
                f.seek(0)

                # Handle Open-Meteo style CSVs that have comment lines at top
                lines = f.readlines()
                
                # Find where actual data starts (skip comment lines starting with #)
                data_start = 0
                for i, line in enumerate(lines):
                    if not line.startswith("#") and line.strip():
                        data_start = i
                        break

                data_lines = lines[data_start:]
                if not data_lines:
                    result["error"] = "No data rows found"
                    return result

                reader = csv.reader(data_lines, delimiter=result["delimiter"])
                rows = list(reader)

                if rows:
                    result["columns"] = rows[0] if rows else None
                    result["num_columns"] = len(rows[0]) if rows else 0
                    result["num_rows"] = len(rows) - 1  # minus header
                    result["encoding"] = encoding
                    result["is_valid_csv"] = True
                    return result

        except UnicodeDecodeError:
            continue
        except Exception as e:
            result["error"] = str(e)
            return result

    result["error"] = "Could not decode file with any supported encoding"
    return result


def is_likely_csv(filepath: Path) -> bool:
    """Quick check if a file looks like a CSV."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            first_line = f.readline()
            # Check for HTML
            if first_line.strip().startswith(("<!DOCTYPE", "<html", "<HTML")):
                return False
            # Check for common CSV patterns (commas or tabs)
            return "," in first_line or "\t" in first_line
    except Exception:
        return False
