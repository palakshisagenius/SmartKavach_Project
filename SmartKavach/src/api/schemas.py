# schemas.py
# Request and response data models for SmartKavach API

from pydantic import BaseModel
from typing import Optional

class TrainEvent(BaseModel):
    train_id: str
    section_id: str
    speed_kmh: float
    signal_aspect: str
    rfid_read_success: int
    radio_packet_loss_pct: float
    weather_index: float
    freight_load_tonnes: float
    deceleration_rate: float
    section_speed_limit: float
    section_incident_rate: float

class MAPrediction(BaseModel):
    train_id: str
    predicted_ma_metres: float
    confidence: str
    fallback_used: bool

class AnomalyResult(BaseModel):
    train_id: str
    is_anomaly: bool
    anomaly_score: float
    severity: str
    description: str

class SpeedAdvisory(BaseModel):
    train_id: str
    section_id: str
    advisory_speed_kmh: float
    section_limit_kmh: float
    reduction_reason: str