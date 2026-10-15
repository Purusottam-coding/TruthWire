import sys
import os

# Set UTF-8
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    print("✓ Health endpoint OK:", data)

def test_countries():
    res = client.get("/api/v1/countries")
    assert res.status_code == 200
    countries = res.json()
    iso_codes = [c["iso2"] for c in countries]
    assert "NP" in iso_codes and "US" in iso_codes and "CA" in iso_codes
    print("✓ Countries endpoint OK (NP, US, CA):", iso_codes)

def test_nepal_dual_feeds():
    # Latest feed
    res_latest = client.get("/api/v1/news?country=NP&feed=latest")
    assert res_latest.status_code == 200
    data_latest = res_latest.json()
    print(f"✓ Nepal Latest feed count: {data_latest['total']}")
    assert data_latest["total"] >= 5

    # Verified feed
    res_verified = client.get("/api/v1/news?country=NP&feed=verified")
    assert res_verified.status_code == 200
    data_verified = res_verified.json()
    print(f"✓ Nepal Verified feed count: {data_verified['total']}")
    assert data_verified["total"] >= 4
    for s in data_verified["items"]:
        assert s["state"] == "verified_summary"
        assert s["image_url"] is not None
        assert s["full_content"] is not None
        print(f"  - Verified Story with Image: {s['display_title'][:40]}... (Claims: {s['claims_count']})")

def test_nrb_forex_rates():
    res = client.get("/api/v1/forex/rates")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    rates = data.get("rates", [])
    assert len(rates) >= 5
    currencies = [r["currency"] for r in rates]
    assert "USD" in currencies and "INR" in currencies and "EUR" in currencies
    print(f"✓ NRB Forex endpoint OK ({data['source']}): Found {len(rates)} currencies (USD, EUR, INR, etc.)")

def test_admin_review_queue():
    res = client.get("/api/v1/admin/review-queue?country=NP")
    assert res.status_code == 200
    queue = res.json()
    print(f"✓ Admin review queue for NP: {len(queue)} pending claims")
    assert len(queue) >= 1

def test_history_feed():
    res = client.get("/api/v1/news?country=NP&feed=history")
    assert res.status_code == 200
    data = res.json()
    print(f"✓ Nepal History feed count: {data['total']}")
    assert data["total"] >= 1
    for s in data["items"]:
        print(f"  - Archived Story: {s['display_title'][:40]}... (Date: {s['first_seen_at']})")

def test_refresh_live():
    res = client.post("/api/v1/news/refresh-live?country=NP")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] is not None
    print(f"✓ Refresh Live Ingestion OK: Ingested '{data['display_title'][:45]}...'")

if __name__ == "__main__":
    test_health()
    test_countries()
    test_nepal_dual_feeds()
    test_history_feed()
    test_refresh_live()
    test_nrb_forex_rates()
    test_admin_review_queue()
    print("\nAll updated API tests PASSED successfully!")
