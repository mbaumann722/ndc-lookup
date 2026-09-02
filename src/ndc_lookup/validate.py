"""Validation status logic, kept separate from the API client so it's
independently testable without network access."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Iterator

from .client import NDCRecord, lookup_ndc


class Status:
    ACTIVE = "ACTIVE"
    DISCONTINUED = "DISCONTINUED"
    NOT_FOUND = "NOT_FOUND"


@dataclass
class ValidationResult:
    ndc: str
    status: str
    brand_name: str | None = None
    labeler_name: str | None = None
    marketing_end_date: str | None = None
    note: str = ""


def _parse_fda_date(value: str | None) -> date | None:
    """openFDA dates are YYYYMMDD strings, or absent."""
    if not value:
        return None
    return datetime.strptime(value, "%Y%m%d").date()


def classify(record: NDCRecord | None, ndc: str) -> ValidationResult:
    if record is None:
        return ValidationResult(ndc=ndc, status=Status.NOT_FOUND,
                                 note="No matching product_ndc in openFDA — check formatting")

    end = _parse_fda_date(record.marketing_end_date)
    if end is not None and end <= date.today():
        return ValidationResult(
            ndc=ndc,
            status=Status.DISCONTINUED,
            brand_name=record.brand_name,
            labeler_name=record.labeler_name,
            marketing_end_date=record.marketing_end_date,
            note=f"Marketing end date {end.isoformat()} has passed",
        )

    return ValidationResult(
        ndc=ndc,
        status=Status.ACTIVE,
        brand_name=record.brand_name,
        labeler_name=record.labeler_name,
        marketing_end_date=record.marketing_end_date,
    )


def validate_one(ndc: str) -> ValidationResult:
    record = lookup_ndc(ndc)
    return classify(record, ndc)


def validate_batch(ndcs: Iterable[str]) -> Iterator[ValidationResult]:
    for ndc in ndcs:
        yield validate_one(ndc)


def read_ndc_column(csv_path: Path, column: str = "ndc") -> list[str]:
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        if column not in (reader.fieldnames or []):
            raise ValueError(f"Column '{column}' not found in {csv_path} (found {reader.fieldnames})")
        return [row[column].strip() for row in reader if row[column].strip()]


def write_report(results: Iterable[ValidationResult], out_path: Path) -> None:
    results = list(results)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["ndc", "status", "brand_name", "labeler_name", "marketing_end_date", "note"],
        )
        writer.writeheader()
        for r in results:
            writer.writerow(vars(r))
