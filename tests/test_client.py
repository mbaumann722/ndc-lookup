import pytest

from ndc_lookup.client import normalize_ndc


def test_normalize_ndc_accepts_standard_dashed_format():
    assert normalize_ndc(" 0069-3060-04 ") == "0069-3060-04"


def test_normalize_ndc_rejects_garbage():
    with pytest.raises(ValueError):
        normalize_ndc("not-an-ndc")


def test_normalize_ndc_rejects_undashed():
    with pytest.raises(ValueError):
        normalize_ndc("0069306004")
