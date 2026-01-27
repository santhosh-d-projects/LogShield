import time
import json
import os
import pandas as pd
import joblib
from datetime import datetime

LOG_FILE = "logs/system_logs.jsonl"

MODEL_FILE = "models/root_cause_model.pkl"
ENC_FILE = "models/label_encoder.pkl"

MAX_LINES = 5000
POLL_SEC = 10


print("\n🚀 Real-Time Failure Prediction Engine Started")
print("📂 Monitoring:", LOG_FILE)
print("⏱ Poll interval:", POLL_SEC, "seconds\n")

# Load model
model = joblib.load(MODEL_FILE)
le = joblib.load(ENC_FILE)


def read_recent_logs(max_lines=MAX_LINES):
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame()

    rows = []

    with open(LOG_FILE, encoding="utf-8") as f:
        lines = f.readlines()[-max_lines:]

    for line in lines:
        try:
            r = json.loads(line)
            r["timestamp"] = pd.to_datetime(
                r.get("timestamp"),
                format="mixed",
                errors="coerce"
            )
            rows.append(r)
        except:
            pass

    return pd.DataFrame(rows)


def make_features(df):
    if len(df) < 50:
        return None

    df["is_error"] = (df["level"] == "ERROR").astype(int)
    df["is_warn"] = (df["level"] == "WARN").astype(int)

    return pd.DataFrame([{
        "count": len(df),
        "cpu_avg": df["cpu"].mean(),
        "cpu_max": df["cpu"].max(),
        "mem_avg": df["memory"].mean(),
        "resp_avg": df["response_time_ms"].mean(),
        "errors": df["is_error"].sum(),
        "warns": df["is_warn"].sum(),
    }])


while True:
    df = read_recent_logs()

    feats = make_features(df)

    if feats is not None:
        probs = model.predict_proba(feats)[0]
        idx = probs.argmax()

        pred = le.inverse_transform([idx])[0]
        conf = probs[idx]

        ts = datetime.now().strftime("%H:%M:%S")

        if pred != "normal":
            print(f"🚨 [{ts}] ALERT → {pred.upper():<15} | confidence = {conf:.2f}")
        else:
            print(f"✅ [{ts}] System healthy | confidence = {conf:.2f}")

    time.sleep(POLL_SEC)
