from pathlib import Path

from ndc_lookup.crosswalk import has_hcpcs_match, load_crosswalk

SAMPLE = Path(__file__).parent.parent / "data" / "sample_crosswalk.csv"


def test_load_crosswalk_reads_sample_file():
    mapping = load_crosswalk(SAMPLE)
    assert mapping["0069-3060-04"] == "J3490"


def test_has_hcpcs_match_hit_and_miss():
    mapping = load_crosswalk(SAMPLE)
    assert has_hcpcs_match("0069-3060-04", mapping) == "J3490"
    assert has_hcpcs_match("not-in-file", mapping) is None
