"""Tests for validate.py — deliberately network-free by constructing
NDCRecord objects directly instead of calling openFDA."""

from datetime import date, timedelta

from ndc_lookup.client import NDCRecord
from ndc_lookup.validate import Status, classify


def _record(**overrides) -> NDCRecord:
    defaults = dict(
        ndc="0069-3060-04",
        product_ndc="0069-3060",
        brand_name="Example Drug",
        labeler_name="Example Labeler",
        marketing_category="NDA",
        marketing_start_date="20100101",
        marketing_end_date=None,
        finished=True,
    )
    defaults.update(overrides)
    return NDCRecord(**defaults)


def test_classify_not_found():
    result = classify(None, "0000-0000-00")
    assert result.status == Status.NOT_FOUND


def test_classify_active_when_no_end_date():
    result = classify(_record(marketing_end_date=None), "0069-3060-04")
    assert result.status == Status.ACTIVE


def test_classify_active_when_end_date_in_future():
    future = (date.today() + timedelta(days=365)).strftime("%Y%m%d")
    result = classify(_record(marketing_end_date=future), "0069-3060-04")
    assert result.status == Status.ACTIVE


def test_classify_discontinued_when_end_date_past():
    past = (date.today() - timedelta(days=1)).strftime("%Y%m%d")
    result = classify(_record(marketing_end_date=past), "0069-3060-04")
    assert result.status == Status.DISCONTINUED
