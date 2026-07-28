# SmartKavach 🚆

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.16-orange)
![Tests](https://img.shields.io/badge/Tests-10%2F10%20passing-brightgreen)
![Validated](https://img.shields.io/badge/Validated-RDSO%20Trial%20Data-blue)

**AI Enhanced Train Collision Avoidance System**

An intelligent overlay on Indian Railways KAVACH, a Train collision avoidance system (TCAS) . Adding predictive Movement Authority computation, real-time anomaly detection, and adaptive speed profiling.

---

## Live Dashboard Preview

<img width="1391" height="925" alt="image" src="https://github.com/user-attachments/assets/bbbe5cd0-83bc-4138-95f1-dbf3b68cb915" />

---

## What this project does

KAVACH is Indian Railways   train collision avoidance system(TCAS). It works well but uses fixed, rule based logic. SmartKavach adds an AI layer on top that:

- **Predicts safe Movement Authority** distances dynamically using weather, load, and track data
- **Detects anomalies in real time**  unusual RFID failures, radio drops, braking patterns  before they become dangerous
- **Generates adaptive speed profiles** per train per section based on current conditions
- **Powers an intelligent NMS dashboard** with fault prediction and live visualisation

---

## Model Performance

| Model | Algorithm | Metric | Result |
|-------|-----------|--------|--------|
| Movement Authority | XGBoost | RMSE | 19.05m |
| Movement Authority | XGBoost | R² | 0.99 |
| Anomaly Detection | LSTM Autoencoder | Recall | 1.00 |
| Anomaly Detection | LSTM Autoencoder | Accuracy | 95% |
| Speed Profiler | Random Forest | RMSE | 0.72 km/h |
| Speed Profiler | Random Forest | R² | 0.9986 |

Validated against real KAVACH RDSO trial data (NCR Division, July 2024) — MA model achieves less than 10% error on real observed values.

---

## Project Structure
```
SmartKavach/
│
├── data/
│   ├── raw/              ← Your real data goes here (not committed to Git)
│   ├── processed/        ← Cleaned, feature engineered data
│   └── synthetic/        ← Simulator-generated training data
│
├── models/
│   ├── saved/            ← Trained model files (.h5, .pkl, .json)
│   └── evaluation/       ← Plots, metrics, reports from model evaluation
│
├── notebooks/            ← Jupyter notebooks for EDA and experimentation
│
├── src/
│   ├── config.py         ← Central settings (reads from .env)
│   ├── simulator/
│   │   └── kavach_simulator.py   ← Synthetic data / live event streamer
│   ├── models/
│   │   ├── ma_model.py           ← Movement Authority prediction (XGBoost)
│   │   ├── anomaly_model.py      ← Anomaly detection (LSTM Autoencoder)
│   │   ├── speed_profiler.py     ← Adaptive speed profiling (Random Forest)
│   │   └── model_loader.py       ← Loads all saved models
│   ├── api/
│   │   ├── main.py               ← FastAPI server
│   │   └── schemas.py            ← Request/response data schemas
│   └── dashboard/        ← React NMS dashboard (added in Phase 3)
│
├── tests/
│   └── test_api.py       ← pytest unit and integration tests
│
├── docs/                 ← SRS, proposal, architecture diagram
│
├── .env.example          ← Copy to .env and fill in your API keys
├── .gitignore
├── requirements.txt

```

---

## Quickstart

`## Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/SmartKavach.git
cd SmartKavach
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your environment file

```bash
cp .env.example .env
# Open .env and add your API keys
```

### 5. Run the API server

```bash
uvicorn src.api.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` to see the interactive API documentation.

### 6. Run the data simulator (in a second terminal)

```bash
python src/simulator/kavach_simulator.py
```

### 7. Run tests

```bash
pytest tests/
```


Visit `http://127.0.0.1:8000/docs` for the API and `http://localhost:5173` for the dashboard.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| ML Models | XGBoost, TensorFlow/Keras (LSTM), scikit-learn |
| API Server | FastAPI, uvicorn, Pydantic |
| Dashboard | React, Recharts |
| Testing | pytest |
| Data | Python, pandas, numpy |

---

## Student Details

| Field | Value |
|-------|-------|
| Name | Palaksh Bhardwaj |
| Programme | B.Tech CSE (Artificial Intelligence) |
| Institution | Gautam Buddha University|


---

## Important Notes

- Never commit your `.env` file — it contains secret API keys
- Model files are excluded from Git by default — retrain from notebooks if needed
- The AI layer is advisory only — it never overrides KAVACH hardware safety commands

  ---

## License

For academic use only. Not for production deployment on live railway systems without formal safety certification.
