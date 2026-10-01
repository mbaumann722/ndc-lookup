"""Tests for lookup_ndc using a fake HTTP response, so no network is needed."""

from ndc_lookup import client


class FakeResponse:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = payload or {}
        self.ok = 200 <= status_code < 300
        self.text = ""

    def json(self):
        return self._payload


TRULICITY = {
    "results": [{
        "product_ndc": "0002-1433",
        "brand_name": "Trulicity",
        "labeler_name": "Eli Lilly and Company",
        "marketing_category": "BLA",
        "marketing_start_date": "20140918",
        "finished": True,
    }]
}


def test_lookup_searches_package_ndc_field(monkeypatch):
    seen = {}

    def fake_get(url, params, timeout):
        seen["search"] = params["search"]
        return FakeResponse(200, TRULICITY)

    monkeypatch.setattr(client.requests, "get", fake_get)
    record = client.lookup_ndc("0002-1433-80")

    assert seen["search"] == 'packaging.package_ndc:"0002-1433-80"'
    assert record.brand_name == "Trulicity"
    assert record.is_active


def test_lookup_returns_none_on_404(monkeypatch):
    monkeypatch.setattr(client.requests, "get", lambda url, params, timeout: FakeResponse(404))
    assert client.lookup_ndc("9999-9999-99") is None
