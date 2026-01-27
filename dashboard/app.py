from flask import Flask, jsonify, render_template
import pandas as pd
import json, os, joblib
from collections import deque
from datetime import datetime

BASE = os.path.dirname(__file__)

LOG_FILE = os.path.join(BASE, "../logs/system_logs.jsonl")
MODEL_FILE = os.path.join(BASE, "../models/root_cause_model.pkl")
ENC_FILE = os.path.join(BASE, "../models/label_encoder.pkl")

MAX_LINES = 3000

app = Flask(__name__)

# =====================
# Predictor Engine
# =====================

class LogPredictor:
    def __init__(self):
        self.model = joblib.load(MODEL_FILE)
        self.encoder = joblib.load(ENC_FILE)

    def read_logs(self):
        if not os.path.exists(LOG_FILE):
            return pd.DataFrame()

        with open(LOG_FILE, encoding="utf-8") as f:
            lines = f.readlines()[-MAX_LINES:]

        rows = []
        for ln in lines:
            try:
                r = json.loads(ln)
                r["timestamp"] = pd.to_datetime(r["timestamp"], errors="coerce", utc=True)
                rows.append(r)
            except:
                pass

        return pd.DataFrame(rows)

    def infer(self):
        df = self.read_logs()

        if df.empty:
            return None

        # Fix: Sync with training window (20s) explicitly
        # We use the latest timestamp in the logs as "now" to handle simulation time correctly
        latest_ts = df["timestamp"].max()
        if pd.isna(latest_ts):
            return None
            
        window_start = latest_ts - pd.Timedelta(seconds=20)
        df_window = df[df["timestamp"] >= window_start].copy() # 20s window for Model
        
        


        # Minimum data points check
        if len(df_window) < 5:
            # Not enough data for valid prediction, fallback or return "System Initializing" logic
            # For now return None to show "Booting" or keep previous
            return None

        df_window["err"] = (df_window.level == "ERROR").astype(int)
        df_window["warn"] = (df_window.level == "WARN").astype(int)

        # Aggregation for Model (20s average)
        feats = pd.DataFrame([{
            "count": len(df_window),
            "cpu_avg": df_window.cpu.mean(),
            "cpu_max": df_window.cpu.max(),
            "mem_avg": df_window.memory.mean(),
            "resp_avg": df_window.response_time_ms.mean(),
            "errors": df_window.err.sum(),
            "warns": df_window.warn.sum(),
        }])
        
        # Predict
        probs = self.model.predict_proba(feats)[0]
        idx = probs.argmax()
        label = self.encoder.inverse_transform([idx])[0]
        confidence = round(float(probs[idx]), 2)

        # Fix for Dashboard: Return INSTANT metrics (last 1-3 seconds)
        # Instead of the window average, we return the very latest log values
        # so the charts feel "live" and reset immediately on refresh.
        last_row = df.iloc[-1]
        
        return {
            "label": label,
            "confidence": confidence,
            "metrics": {
                "cpu": float(last_row["cpu"]),
                "mem": float(last_row["memory"]) / 1024, # Convert MB to GB for UI
                "lat": float(last_row["response_time_ms"])
            }
        }

predictor = LogPredictor()

history = deque(maxlen=12)
metric_stream = deque(maxlen=40)

# =====================
# Routes
# =====================

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/status")
def status():
    out = predictor.infer()

    if not out:
        return jsonify({"status": "Booting"})

    state = "Failure" if out["label"] != "normal" else "Normal"
    timestamp = datetime.now().strftime("%H:%M:%S")

    history.appendleft({
        "time": timestamp,
        "cause": out["label"],
        "confidence": out["confidence"]
    })

    # Add timestamp to metrics
    m = out["metrics"].copy()
    m["time"] = timestamp
    metric_stream.append(m)

    return jsonify({
        "status": state,
        "cause": out["label"],
        "confidence": out["confidence"],
        "metrics": out["metrics"]
    })

@app.route("/api/metrics")
def metrics():
    data = list(metric_stream)
    return jsonify({
        "timestamps": [d.get("time") for d in data],
        "cpu": [d.get("cpu") for d in data],
        "memory": [d.get("mem") for d in data],
        "latency": [d.get("lat") for d in data]
    })

@app.route("/api/history")
def hist():
    return jsonify(list(history))

if __name__ == "__main__":
    app.run(debug=True)

