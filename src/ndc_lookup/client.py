"""Thin client around the public openFDA NDC directory API.

Docs: https://open.fda.gov/apis/drug/ndc/
No API key is required for light, occasional use; openFDA rate-limits
anonymous callers more aggressively than keyed ones.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

import requests

OPENFDA_NDC_ENDPOINT = "https://api.fda.gov/drug/ndc.json"


class OpenFDAError(RuntimeError):
    """Raised when the openFDA API can't be reached or returns an error."""


def normalize_ndc(raw: str) -> str:
    """Strip whitespace/punctuation variants down to digits-and-dashes.

    openFDA accepts NDC codes in their labeled dash format (e.g.
    '0069-3060-04'). This does not attempt full 10-digit-to-11-digit
    format conversion — that's a deliberately separate, well-tested
    concern; see validate.py.
    """
    cleaned = raw.strip()
    if not re.fullmatch(r"\d{4,5}-\d{3,4}-\d{1,2}", cleaned):
        raise ValueError(f"'{raw}' doesn't look like a dashed NDC (e.g. 0069-3060-04)")
    return cleaned


@dataclass
class NDCRecord:
    ndc: str
    product_ndc: Optional[str]
    brand_name: Optional[str]
    labeler_name: Optional[str]
    marketing_category: Optional[str]
    marketing_start_date: Optional[str]
    marketing_end_date: Optional[str]
    finished: Optional[bool]

    @property
    def is_active(self) -> bool:
        """True if there's no end date on record — i.e. still marketed."""
        return self.marketing_end_date is None


def lookup_ndc(ndc: str, *, timeout: float = 10.0) -> Optional[NDCRecord]:
    """Look up a single NDC. Returns None if openFDA has no matching record
    (which usually means the code is a typo, mis-formatted, or was never a
    real product — not necessarily 'discontinued')."""
    ndc = normalize_ndc(ndc)
    resp = requests.get(
        OPENFDA_NDC_ENDPOINT,
        params={"search": f'product_ndc:"{ndc}"', "limit": 1},
        timeout=timeout,
    )
    if resp.status_code == 404:
        # openFDA returns 404 (not an empty list) when nothing matches
        return None
    if not resp.ok:
        raise OpenFDAError(f"openFDA returned {resp.status_code}: {resp.text[:200]}")

    results = resp.json().get("results", [])
    if not results:
        return None

    r = results[0]
    return NDCRecord(
        ndc=ndc,
        product_ndc=r.get("product_ndc"),
        brand_name=r.get("brand_name"),
        labeler_name=r.get("labeler_name"),
        marketing_category=r.get("marketing_category"),
        marketing_start_date=r.get("marketing_start_date"),
        marketing_end_date=r.get("marketing_end_date"),
        finished=r.get("finished"),
    )
