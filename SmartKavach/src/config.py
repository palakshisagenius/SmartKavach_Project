# config.py
# Central configuration for SmartKavach
# Edit values here or override via a .env file

import os
from dotenv import load_dotenv

load_dotenv()

# --- API settings ---
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", 8000))

# --- Model thresholds ---
MA_CONFIDENCE_THRESHOLD = float(os.getenv("MA_CONFIDENCE_THRESHOLD", 0.95))
ANOMALY_THRESHOLD_PERCENTILE = float(os.getenv("ANOMALY_THRESHOLD_PERCENTILE", 95.0))

# --- Simulator settings ---
SIMULATOR_INTERVAL_SECONDS = float(os.getenv("SIMULATOR_INTERVAL", 1.0))
NUM_TRAINS = int(os.getenv("NUM_TRAINS", 5))

# --- Data paths ---
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DATA_SYNTHETIC_DIR = os.path.join(BASE_DIR, "data", "synthetic")
MODELS_DIR = os.path.join(BASE_DIR, "models", "saved")
EVAL_DIR = os.path.join(BASE_DIR, "models", "evaluation")

# --- External APIs ---
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")  # For NMS LLM interface
