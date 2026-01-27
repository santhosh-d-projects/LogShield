# LogShield

**One-line description:** AI-Powered Server Protection Through Intelligent Log Analysis

## Architecture Overview
LogShield is an AIOps solution designed to predict server failures by analyzing system logs in real-time. It leverages machine learning models to detect anomalies and predict potential issues before they cause downtime.
The system consists of:
- **Log Simulator:** Generates synthetic server logs for training and testing.
- **Data Preprocessing:** Cleans and formats raw logs for model consumption.
- **Prediction Engine:** Uses ML models to analyze logs and predict failure probabilities.
- **Dashboard:** A web-based interface for real-time monitoring and visualization.

## How to Run

### 1. Prerequisites
Ensure you have Python installed. It is recommended to use a virtual environment.

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Main System
To start the log generation and prediction system:
```bash
python main.py
```

### 3. Run the Dashboard
To launch the monitoring dashboard:
```bash
python dashboard/app.py
```
Access the dashboard in your browser at `http://127.0.0.1:5000`.

## Folder Structure
```
log_simulator/
├── dashboard/          # Web dashboard (Flask app)
│   ├── static/         # CSS, JS assets
│   └── templates/      # HTML templates
│   └── app.py          # Dashboard entry point
├── logs/               # Generated logs (ignored in git)
├── models/             # Trained ML models (ignored in git)
├── services/           # Business logic services
├── main.py             # Main entry point for log simulation
├── controller.py       # System controller
├── requirements.txt    # Python dependencies
└── ...
```

## Features
- **Real-time Prediction:** continuously monitors logs to predict failure risks.
- **Interactive Dashboard:** Visualizes system health, log trends, and alerts.
- **SHAP Integration:** Explains model predictions for transparency.
- **Failure Injection:** Simulates various failure scenarios to test system robustness.
