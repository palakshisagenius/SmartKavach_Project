# test_api.py
# Unit tests for SmartKavach API
# Run with: pytest tests/

import requests
import pytest

BASE_URL = "http://127.0.0.1:8000"

NORMAL_EVENT = {
    "train_id": "TRAIN-TEST",
    "section_id": "SEC-01",
    "speed_kmh": 80.0,
    "signal_aspect": "green",
    "rfid_read_success": 1,
    "radio_packet_loss_pct": 2.0,
    "weather_index": 0.1,
    "freight_load_tonnes": 500.0,
    "deceleration_rate": 0.6,
    "section_speed_limit": 110.0,
    "section_incident_rate": 0.02
}

ANOMALY_EVENT = {
    "train_id": "TRAIN-ANOMALY",
    "section_id": "SEC-04",
    "speed_kmh": 160.0,
    "signal_aspect": "red",
    "rfid_read_success": 0,
    "radio_packet_loss_pct": 50.0,
    "weather_index": 0.9,
    "freight_load_tonnes": 2900.0,
    "deceleration_rate": 2.5,
    "section_speed_limit": 110.0,
    "section_incident_rate": 0.08
}

# ── Test 1 ────────────────────────────────────────────────────────────────────
def test_api_is_running():
    r = requests.get(BASE_URL)
    assert r.status_code == 200
    assert r.json()["status"] == "SmartKavach API running"
    print("\n✅ Test 1 passed: API is running")

# ── Test 2 ────────────────────────────────────────────────────────────────────
def test_ma_prediction_returns_valid():
    r = requests.post(f"{BASE_URL}/predict/ma", json=NORMAL_EVENT)
    assert r.status_code == 200
    data = r.json()
    assert "predicted_ma_metres" in data
    assert "confidence" in data
    assert data["fallback_used"] == False
    print(f"\n✅ Test 2 passed: MA = {data['predicted_ma_metres']}m")

# ── Test 3 ────────────────────────────────────────────────────────────────────
def test_ma_is_always_positive():
    r = requests.post(f"{BASE_URL}/predict/ma", json=NORMAL_EVENT)
    data = r.json()
    assert data["predicted_ma_metres"] > 0
    print(f"\n✅ Test 3 passed: MA is positive ({data['predicted_ma_metres']}m)")

# ── Test 4 ────────────────────────────────────────────────────────────────────
def test_bad_weather_gives_low_confidence():
    foggy_event = NORMAL_EVENT.copy()
    foggy_event["weather_index"] = 0.9
    r = requests.post(f"{BASE_URL}/predict/ma", json=foggy_event)
    data = r.json()
    assert data["confidence"] == "LOW"
    print(f"\n✅ Test 4 passed: Bad weather → confidence = {data['confidence']}")

# ── Test 5 ────────────────────────────────────────────────────────────────────
def test_speed_advisory_never_exceeds_limit():
    r = requests.post(f"{BASE_URL}/predict/speed", json=NORMAL_EVENT)
    assert r.status_code == 200
    data = r.json()
    assert data["advisory_speed_kmh"] <= NORMAL_EVENT["section_speed_limit"]
    print(f"\n✅ Test 5 passed: Advisory {data['advisory_speed_kmh']} "
          f"<= limit {NORMAL_EVENT['section_speed_limit']}")

# ── Test 6 ────────────────────────────────────────────────────────────────────
def test_speed_advisory_returns_valid():
    r = requests.post(f"{BASE_URL}/predict/speed", json=NORMAL_EVENT)
    data = r.json()
    assert "advisory_speed_kmh" in data
    assert "reduction_reason" in data
    assert data["advisory_speed_kmh"] > 0
    print(f"\n✅ Test 6 passed: Advisory = {data['advisory_speed_kmh']} km/h")

# ── Test 7 ────────────────────────────────────────────────────────────────────
def test_anomaly_endpoint_returns_valid():
    r = requests.post(f"{BASE_URL}/detect/anomaly", json=NORMAL_EVENT)
    assert r.status_code == 200
    data = r.json()
    assert "is_anomaly" in data
    assert "severity" in data
    assert "anomaly_score" in data
    print(f"\n✅ Test 7 passed: Anomaly endpoint working")

# ── Test 8 ────────────────────────────────────────────────────────────────────
def test_anomaly_fires_after_30_events():
    detected = False
    for i in range(35):
        r = requests.post(
            f"{BASE_URL}/detect/anomaly",
            json=ANOMALY_EVENT
        )
        data = r.json()
        if data["is_anomaly"]:
            detected = True
            print(f"\n✅ Test 8 passed: Anomaly detected at event {i+1}")
            print(f"   Severity: {data['severity']}")
            break
    assert detected, "Anomaly was never detected after 35 events"

# ── Test 9 ────────────────────────────────────────────────────────────────────
def test_invalid_signal_aspect_rejected():
    bad_event = NORMAL_EVENT.copy()
    bad_event["signal_aspect"] = "purple"
    r = requests.post(f"{BASE_URL}/predict/ma", json=bad_event)
    assert r.status_code == 500
    print(f"\n✅ Test 9 passed: Invalid signal aspect rejected")

# ── Test 10 ───────────────────────────────────────────────────────────────────
def test_missing_field_rejected():
    incomplete_event = {"train_id": "TRAIN-TEST", "speed_kmh": 80.0}
    r = requests.post(f"{BASE_URL}/predict/ma", json=incomplete_event)
    assert r.status_code == 422
    print(f"\n✅ Test 10 passed: Missing fields correctly rejected (422)")