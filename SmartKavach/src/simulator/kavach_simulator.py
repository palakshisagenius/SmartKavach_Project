# kavach_simulator.py
# Generates synthetic KAVACH train event data for SmartKavach
# Run this file directly to generate and save the dataset

import random
import csv
import os
from datetime import datetime, timedelta

# ── Settings ────────────────────────────────────────────────────────────────
NUM_TRAINS        = 10
EVENTS_PER_TRAIN  = 1000
ANOMALY_RATE      = 0.05
OUTPUT_DIR        = os.path.join(os.path.dirname(__file__), "../../data/synthetic")
OUTPUT_FILE       = os.path.join(OUTPUT_DIR, "kavach_synthetic.csv")

# ── Track sections ──────────────────────────────────────────────────────────
SECTIONS = [
    {"id": "SEC-01", "speed_limit": 110, "incident_rate": 0.02},
    {"id": "SEC-02", "speed_limit": 100, "incident_rate": 0.05},
    {"id": "SEC-03", "speed_limit": 130, "incident_rate": 0.01},
    {"id": "SEC-04", "speed_limit":  90, "incident_rate": 0.08},
    {"id": "SEC-05", "speed_limit": 120, "incident_rate": 0.03},
]

SIGNAL_ASPECTS = ["green", "yellow", "red"]

def random_weather():
    return round(random.choices(
        [random.uniform(0.0, 0.2),
         random.uniform(0.2, 0.5),
         random.uniform(0.5, 1.0)],
        weights=[0.70, 0.20, 0.10]
    )[0], 3)

def signal_from_speed(speed, limit):
    ratio = speed / limit
    if ratio < 0.5:
        return "red"
    elif ratio < 0.85:
        return "yellow"
    else:
        return "green"

def compute_ma(speed, signal, weather, load, section_limit):
    speed_ms = speed / 3.6
    base_ma  = (speed_ms ** 2) / (2 * 0.6)
    signal_factor  = {"green": 1.0, "yellow": 0.7, "red": 0.3}[signal]
    weather_factor = 1.0 - (weather * 0.3)
    load_factor    = 1.0 - (min(load, 3000) / 3000 * 0.2)
    ma = base_ma * signal_factor * weather_factor * load_factor
    ma += random.gauss(0, 15)
    return round(max(50, ma), 1)

def generate_event(train_id, timestamp, section, is_anomaly=False):
    limit = section["speed_limit"]

    if is_anomaly:
        anomaly_type = random.choice(["rfid_fail", "radio_drop", "overspeed", "sudden_brake"])
        if anomaly_type == "rfid_fail":
            speed = round(random.uniform(60, limit), 1)
            signal = signal_from_speed(speed, limit)
            rfid_success = False
            packet_loss = round(random.uniform(0, 5), 2)
            weather = random_weather()
            load = round(random.uniform(200, 3000), 1)
            decel_rate = round(random.uniform(0.3, 0.7), 3)
        elif anomaly_type == "radio_drop":
            speed = round(random.uniform(60, limit), 1)
            signal = signal_from_speed(speed, limit)
            rfid_success = True
            packet_loss = round(random.uniform(20, 60), 2)
            weather = random_weather()
            load = round(random.uniform(200, 3000), 1)
            decel_rate = round(random.uniform(0.3, 0.7), 3)
        elif anomaly_type == "overspeed":
            speed = round(random.uniform(limit * 1.1, limit * 1.4), 1)
            signal = "green"
            rfid_success = True
            packet_loss = round(random.uniform(0, 5), 2)
            weather = random_weather()
            load = round(random.uniform(200, 3000), 1)
            decel_rate = round(random.uniform(0.3, 0.7), 3)
        else:
            speed = round(random.uniform(10, 40), 1)
            signal = "red"
            rfid_success = True
            packet_loss = round(random.uniform(0, 5), 2)
            weather = random_weather()
            load = round(random.uniform(200, 3000), 1)
            decel_rate = round(random.uniform(1.5, 3.0), 3)
    else:
        anomaly_type = "none"
        speed = round(random.uniform(40, limit * 0.95), 1)
        signal = signal_from_speed(speed, limit)
        rfid_success = random.random() > 0.02
        packet_loss = round(random.uniform(0, 8), 2)
        weather = random_weather()
        load = round(random.uniform(200, 3000), 1)
        decel_rate = round(random.uniform(0.4, 0.8), 3)

    ma = compute_ma(speed, signal, weather, load, limit)
    advisory_speed = round(min(
        limit,
        speed * (1.0 - weather * 0.2) * (1.0 - min(load, 3000) / 3000 * 0.1)
    ), 1)

    return {
        "timestamp":             timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "train_id":              train_id,
        "section_id":            section["id"],
        "section_speed_limit":   limit,
        "speed_kmh":             speed,
        "signal_aspect":         signal,
        "rfid_read_success":     int(rfid_success),
        "radio_packet_loss_pct": packet_loss,
        "weather_index":         weather,
        "freight_load_tonnes":   load,
        "deceleration_rate":     decel_rate,
        "section_incident_rate": section["incident_rate"],
        "movement_authority_m":  ma,
        "advisory_speed_kmh":    advisory_speed,
        "is_anomaly":            int(is_anomaly),
        "anomaly_type":          anomaly_type,
    }

def generate_dataset():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_events = []
    start_time = datetime(2024, 1, 1, 6, 0, 0)

    print("\n SmartKavach Synthetic Data Generator")
    print(f"   Trains:        {NUM_TRAINS}")
    print(f"   Events/train:  {EVENTS_PER_TRAIN}")
    print(f"   Total rows:    {NUM_TRAINS * EVENTS_PER_TRAIN}")
    print(f"   Anomaly rate:  {ANOMALY_RATE * 100:.0f}%\n")

    for t in range(NUM_TRAINS):
        train_id  = f"TRAIN-{t+1:02d}"
        section   = random.choice(SECTIONS)
        timestamp = start_time + timedelta(hours=t * 2)
        anomaly_count = 0

        for e in range(EVENTS_PER_TRAIN):
            is_anomaly = random.random() < ANOMALY_RATE
            if is_anomaly:
                anomaly_count += 1
            event = generate_event(train_id, timestamp, section, is_anomaly)
            all_events.append(event)
            timestamp += timedelta(seconds=random.randint(5, 15))
            if e % 100 == 0 and e > 0:
                section = random.choice(SECTIONS)

        print(f"   Done: {train_id} — {EVENTS_PER_TRAIN} events, {anomaly_count} anomalies")

    random.shuffle(all_events)

    fieldnames = all_events[0].keys()
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_events)

    total_anomalies = sum(e["is_anomaly"] for e in all_events)
    print(f"\n Dataset saved: {OUTPUT_FILE}")
    print(f"   Total rows:     {len(all_events)}")
    print(f"   Total anomalies:{total_anomalies} ({total_anomalies/len(all_events)*100:.1f}%)")
    print("\n Next step: open notebooks/ and run the EDA notebook!")

if __name__ == "__main__":
    generate_dataset()
