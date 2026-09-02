"""Optional local HCPCS-to-NDC crosswalk matching.

CMS publishes a real crosswalk quarterly; this module just expects a CSV
shaped the same way (columns: ndc, hcpcs_code, hcpcs_description) so the
matching logic is realistic without shipping any real CMS file.
"""

from __future__ import annotations

import csv
from pathlib import Path


def load_crosswalk(csv_path: Path) -> dict[str, str]:
    """Returns a dict of NDC -> HCPCS code."""
    mapping: dict[str, str] = {}
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapping[row["ndc"].strip()] = row["hcpcs_code"].strip()
    return mapping


def has_hcpcs_match(ndc: str, crosswalk: dict[str, str]) -> str | None:
    """Returns the HCPCS code if this NDC has a billable crosswalk entry,
    else None."""
    return crosswalk.get(ndc)
