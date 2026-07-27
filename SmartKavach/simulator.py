# simulator.py
# Streams live train events to the SmartKavach API
# Simulates real KAVACH hardware sending data

import requests
import random
import time
import json
from datetime import datetime

# ── Settings ─────────────────────────────────────────────────────────────────
API_URL        = "http://127.0.0.1:8000"
INTERVAL       = 1.0       # seconds between events
NUM_TRAINS     = 3         # trains to simulate simultaneously

# ── Track sections ────────────────────────────────────────────────────────────
SECTIONS = [
    {"id": "SEC-01", "speed_limit": 110, "incident_rate": 0.02},
    {"id": "SEC-02", "speed_limit": 100, "incident_rate": 0.05},
    {"id": "SEC-03", "speed_limit": 130, "incident_rate": 0.01},
]

# ── Train state ───────────────────────────────────────────────────────────────
trains = {}
for i in range(NUM_TRAINS):
    tid = f"TRAIN-{i+1:02d}"
    trains[tid] = {
        "section": random.choice(SECTIONS),
        "inject_anomaly": False,
        "anomaly_countdown": 0
    }

def generate_event(train_id, inject_anomaly=False):
    section = trains[train_id]["section"]
    limit   = section["speed_limit"]

    if inject_anomaly:
        return {
            "train_id":              train_id,
            "section_id":            section["id"],
            "speed_kmh":             round(random.uniform(limit*1.1, limit*1.4), 1),
            "signal_aspect":         "red",
            "rfid_read_success":     0,
            "radio_packet_loss_pct": round(random.uniform(25, 60), 2),
            "weather_index":         round(random.uniform(0.7, 1.0), 3),
            "freight_load_tonnes":   round(random.uniform(2000, 3000), 1),
            "deceleration_rate":     round(random.uniform(1.5, 3.0), 3),
            "section_speed_limit":   limit,
            "section_incident_rate": section["incident_rate"]
        }
    else:
        speed = round(random.uniform(40, limit * 0.95), 1)
        ratio = speed / limit
        signal = "green" if ratio > 0.85 else "yellow" if ratio > 0.5 else "red"
        return {
            "train_id":              train_id,
            "section_id":            section["id"],
            "speed_kmh":             speed,
            "signal_aspect":         signal,
            "rfid_read_success":     1,
            "radio_packet_loss_pct": round(random.uniform(0, 8), 2),
            "weather_index":         round(random.uniform(0.0, 0.3), 3),
            "freight_load_tonnes":   round(random.uniform(200, 1500), 1),
            "deceleration_rate":     round(random.uniform(0.4, 0.8), 3),
            "section_speed_limit":   limit,
            "section_incident_rate": section["incident_rate"]
        }

def send_event(train_id, event):
    try:
        # Send to all three endpoints
        ma_r     = requests.post(f"{API_URL}/predict/ma",      json=event, timeout=3)
        speed_r  = requests.post(f"{API_URL}/predict/speed",   json=event, timeout=3)
        anomaly_r= requests.post(f"{API_URL}/detect/anomaly",  json=event, timeout=3)

        ma      = ma_r.json()
        speed   = speed_r.json()
        anomaly = anomaly_r.json()

        now = datetime.now().strftime("%H:%M:%S")

        # Print results
        print(f"\n[{now}] {train_id} | Section: {event['section_id']} | Speed: {event['speed_kmh']} km/h")
        print(f"  MA:      {ma['predicted_ma_metres']}m  (confidence: {ma['confidence']})")
        print(f"  Speed:   {speed['advisory_speed_kmh']} km/h advisory  ({speed['reduction_reason']})")

        if anomaly['is_anomaly']:
            print(f"  ⚠️  ANOMALY: {anomaly['severity']} — {anomaly['description']}")
        else:
            print(f"  Anomaly: {anomaly['description']}")

    except Exception as e:
        print(f"  Error: {e}")

# ── Main loop ─────────────────────────────────────────────────────────────────
print("🚆 SmartKavach Live Simulator Starting...")
print(f"   Simulating {NUM_TRAINS} trains")
print(f"   API: {API_URL}")
print(f"   Press Ctrl+C to stop\n")
print("=" * 60)

tick = 0
try:
    while True:
        tick += 1

        # Every 60 seconds inject an anomaly into TRAIN-01
        if tick % 60 == 0:
            print(f"\n🔴 INJECTING ANOMALY into TRAIN-01 for 35 events...")
            trains["TRAIN-01"]["inject_anomaly"]   = True
            trains["TRAIN-01"]["anomaly_countdown"] = 35

        for train_id in trains:
            state = trains[train_id]

            # Check anomaly injection
            inject = state["inject_anomaly"]
            if inject:
                state["anomaly_countdown"] -= 1
                if state["anomaly_countdown"] <= 0:
                    state["inject_anomaly"] = False
                    print(f"\n✅ Anomaly injection ended for {train_id}")

            event = generate_event(train_id, inject_anomaly=inject)
            send_event(train_id, event)

        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print("\n\nSimulator stopped.")