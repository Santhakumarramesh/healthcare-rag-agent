"""
Medical Report Parser for extracting structured lab values.
"""
from __future__ import annotations

import re
from typing import List, Dict, Optional


LAB_LINE_PATTERN = re.compile(
    r"(?P<name>[A-Za-z][A-Za-z0-9\s\-/()]+?)\s*[:\-]?\s+"
    r"(?P<value>\d+(?:\.\d+)?)\s*"
    r"(?P<unit>[A-Za-z/%\^\d\.]+)?"
    r"(?:\s*\(?(?:ref|range)?[:\s]*"
    r"(?P<reference>[<>]?\s*\d+(?:\.\d+)?\s*[-–]\s*\d+(?:\.\d+)?|[<>]\s*\d+(?:\.\d+)?)\)?)?",
    re.IGNORECASE,
)


def _parse_reference_bounds(reference: Optional[str]):
    """Parse reference range into low and high bounds."""
    if not reference:
        return None, None

    ref = reference.replace("–", "-").replace(" ", "")
    if "-" in ref:
        low, high = ref.split("-", 1)
        try:
            return float(low.replace("<", "").replace(">", "")), float(high)
        except ValueError:
            return None, None

    if ref.startswith("<"):
        try:
            return None, float(ref[1:])
        except ValueError:
            return None, None

    if ref.startswith(">"):
        try:
            return float(ref[1:]), None
        except ValueError:
            return None, None

    return None, None


def infer_flag(value: str, reference: Optional[str]) -> Optional[str]:
    """Infer if value is normal, high, or low based on reference range."""
    try:
        numeric_value = float(value)
    except ValueError:
        return None

    low, high = _parse_reference_bounds(reference)

    if low is not None and numeric_value < low:
        return "Low"
    if high is not None and numeric_value > high:
        return "High"
    return "Normal"


def parse_report_text(text: str) -> List[Dict]:
    """
    Parse medical report text to extract structured lab values.
    
    Args:
        text: Raw report text
        
    Returns:
        List of extracted values with name, value, unit, reference, flag
    """
    extracted = []

    for line in text.splitlines():
        line = line.strip()
        if not line or len(line) < 3:
            continue

        match = LAB_LINE_PATTERN.search(line)
        if not match:
            continue

        name = match.group("name").strip()
        value = match.group("value").strip()
        unit = (match.group("unit") or "").strip() or None
        reference = (match.group("reference") or "").strip() or None

        flag = infer_flag(value, reference)

        extracted.append({
            "name": name,
            "value": value,
            "unit": unit,
            "reference": reference,
            "flag": flag,
        })

    # Deduplicate by (name, value)
    seen = set()
    unique_rows = []
    for item in extracted:
        key = (item["name"].lower(), item["value"])
        if key not in seen:
            seen.add(key)
            unique_rows.append(item)

    return unique_rows
