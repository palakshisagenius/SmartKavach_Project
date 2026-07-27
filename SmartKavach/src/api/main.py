# main.py
# SmartKavach FastAPI inference server

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import joblib
import os
from src.api.schemas import TrainEvent, MAPrediction, AnomalyResult, SpeedAdvisory

# ── Load all models ──────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MODELS_DIR  = os.path.join(BASE_DIR, "models", "saved")

print("Loading models...")

# MA model
ma_model   = joblib.load(os.path.join(MODELS_DIR, "ma_model.pkl"))
ma_encoder = joblib.load(os.path.join(MODELS_DIR, "ma_label_encoder.pkl"))
print("✅ MA model loaded")

# Anomaly model
from tensorflow.keras.models import load_model
anomaly_model = load_model(os.path.join(MODELS_DIR, "anomaly_model.keras"))
anomaly_scaler    = joblib.load(os.path.join(MODELS_DIR, "anomaly_scaler.pkl"))
anomaly_threshold = joblib.load(os.path.join(MODELS_DIR, "anomaly_threshold.pkl"))
print("✅ Anomaly model loaded")

# Speed profiler
speed_model = joblib.load(os.path.join(MODELS_DIR, "speed_profiler.pkl"))
print("✅ Speed profiler loaded")

print("\n🚆 All models ready!\n")

# ── App setup ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="SmartKavach API",
    description="AI inference layer for KAVACH train collision avoidance",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store recent events for anomaly detection window
recent_events = {}

# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "status": "SmartKavach API running",
        "models": ["MA Prediction", "Anomaly Detection", "Speed Profiler"],
        "version": "1.0.0"
    }

@app.post("/predict/ma", response_model=MAPrediction)
def predict_ma(event: TrainEvent):
    try:
        signal_encoded = ma_encoder.transform([event.signal_aspect])[0]
        features = np.array([[
            event.speed_kmh,
            signal_encoded,
            event.weather_index,
            event.freight_load_tonnes,
            event.section_speed_limit,
            event.section_incident_rate,
            event.rfid_read_success,
            event.radio_packet_loss_pct,
            event.deceleration_rate
        ]])
        ma = float(ma_model.predict(features)[0])
        ma = max(50.0, ma)

        if event.weather_index > 0.7:
            confidence = "LOW"
        elif event.weather_index > 0.4:
            confidence = "MEDIUM"
        else:
            confidence = "HIGH"

        return MAPrediction(
            train_id=event.train_id,
            predicted_ma_metres=round(ma, 1),
            confidence=confidence,
            fallback_used=False
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect/anomaly", response_model=AnomalyResult)
def detect_anomaly(event: TrainEvent):
    try:
        train_id = event.train_id

        # Store event in recent window
        if train_id not in recent_events:
            recent_events[train_id] = []

        recent_events[train_id].append([
            event.speed_kmh,
            event.rfid_read_success,
            event.radio_packet_loss_pct,
            event.weather_index,
            event.freight_load_tonnes,
            event.deceleration_rate
        ])

        # Keep only last 31 events
        if len(recent_events[train_id]) > 31:
            recent_events[train_id].pop(0)

        # Need at least 30 events to detect
        if len(recent_events[train_id]) < 30:
            return AnomalyResult(
                train_id=train_id,
                is_anomaly=False,
                anomaly_score=0.0,
                severity="INFO",
                description=f"Collecting data ({len(recent_events[train_id])}/30 events)"
            )

        # Run anomaly detection
        sequence = np.array(recent_events[train_id][-30:])
        sequence_scaled = anomaly_scaler.transform(sequence)
        sequence_input  = sequence_scaled.reshape(1, 30, 6)

        reconstruction  = anomaly_model.predict(sequence_input, verbose=0)
        error = float(np.mean(np.abs(reconstruction - sequence_input)))
        is_anomaly = error > anomaly_threshold

        if is_anomaly:
            if error > anomaly_threshold * 3:
                severity = "CRITICAL"
            elif error > anomaly_threshold * 1.5:
                severity = "WARNING"
            else:
                severity = "INFO"
            description = f"Anomaly detected! Error {error:.4f} exceeds threshold {anomaly_threshold:.4f}"
        else:
            severity = "INFO"
            description = "Normal operation"

        return AnomalyResult(
            train_id=train_id,
            is_anomaly=bool(is_anomaly),
            anomaly_score=round(error, 6),
            severity=severity,
            description=description
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/speed", response_model=SpeedAdvisory)
def predict_speed(event: TrainEvent):
    try:
        features = np.array([[
            event.speed_kmh,
            event.weather_index,
            event.freight_load_tonnes,
            event.section_speed_limit,
            event.section_incident_rate,
            event.deceleration_rate,
            event.rfid_read_success
        ]])

        advisory = float(speed_model.predict(features)[0])
        advisory = min(advisory, event.section_speed_limit)
        advisory = max(0.0, advisory)

        if event.weather_index > 0.5:
            reason = "Adverse weather conditions"
        elif event.freight_load_tonnes > 2000:
            reason = "Heavy freight load"
        elif event.section_incident_rate > 0.05:
            reason = "High incident rate section"
        else:
            reason = "Normal operating conditions"

        return SpeedAdvisory(
            train_id=event.train_id,
            section_id=event.section_id,
            advisory_speed_kmh=round(advisory, 1),
            section_limit_kmh=event.section_speed_limit,
            reduction_reason=reason
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))