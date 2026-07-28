# SmartKavach 🚆

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.16-orange)
![Tests](https://img.shields.io/badge/Tests-10%2F10%20passing-brightgreen)
![Validated](https://img.shields.io/badge/Validated-RDSO%20Trial%20Data-blue)

**AI-Enhanced Train Collision Avoidance System**

An intelligent overlay on Indian Railways KAVACH, a Train collision avoidance system (TCAS) , adding predictive Movement Authority computation, real-time anomaly detection, and adaptive speed profiling.

---

## Live Dashboard Preview

![SmartKavach NMS Dashboard](docs/dashboard_screenshot.png)

---

## What this project does

KAVACH is Indian Railways   train collision avoidance system(TCAS). It works well but uses fixed, rule based logic. SmartKavach adds an AI layer on top that:

- **Predicts safe Movement Authority** distances dynamically using weather, load, and track data
- **Detects anomalies in real time**  unusual RFID failures, radio drops, braking patterns — before they become dangerous
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

SmartKavach/
├── data/
│ ├── raw/ ← Real data (not committed to Git)
│ ├── processed/ ← Cleaned, feature-engineered data
│ └── synthetic/ ← Simulator-generated training data
├── models/
│ ├── saved/ ← Trained model files (.h5, .pkl, .json)
│ └── evaluation/ ← Plots and metrics
├── notebooks/ ← Jupyter notebooks for EDA and training
├── src/
│ ├── config.py ← Central settings
│ ├── simulator/ ← Synthetic data / live event streamer
│ ├── models/ ← MA, anomaly, speed profiler modules
│ └── api/ ← FastAPI server and schemas
├── tests/ ← pytest unit and integration tests
├── docs/ ← SRS, proposal, architecture, report
├── dashboard/ ← React NMS dashboard
└── requirements.txt

---

## Quickstart

```bash
# 1. Clone
git clone https://github.com/palakshisagenius/SmartKavach_Project.git
cd SmartKavach_Project/SmartKavach

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the API server
python -m uvicorn src.api.main:app --reload

# 5. Run the dashboard
cd dashboard
npm install
npm run dev
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