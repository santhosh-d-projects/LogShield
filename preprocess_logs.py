import json
import pandas as pd
from datetime import datetime

LOG_FILE = "logs/system_logs.jsonl"
OUT_FILE = "data/features.csv"

WINDOW_SEC = 20   # sliding window size


def load_logs():
    rows = []
    bad = 0
    with open(LOG_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                bad += 1

    print(f"⚠ Skipped {bad} bad lines")

    return pd.DataFrame(rows)



def preprocess(df):
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        format="mixed",
        errors="coerce"
    )

    # drop rows where timestamp couldn't be parsed
    df = df.dropna(subset=["timestamp"])

    df = df.sort_values("timestamp")

    df["is_error"] = (df["level"] == "ERROR").astype(int)
    df["is_warn"] = (df["level"] == "WARN").astype(int)

    return df


def window_features(df):
    feats = []

    start = df["timestamp"].min()
    end = df["timestamp"].max()

    t = start

    while t < end:
        w = df[(df["timestamp"] >= t) &
               (df["timestamp"] < t + pd.Timedelta(seconds=WINDOW_SEC))]

        if len(w) == 0:
            t += pd.Timedelta(seconds=WINDOW_SEC)
            continue

        label = w["failure_mode"].mode()[0]

        feats.append({
            "window_start": t,
            "count": len(w),
            "cpu_avg": w["cpu"].mean(),
            "cpu_max": w["cpu"].max(),
            "mem_avg": w["memory"].mean(),
            "resp_avg": w["response_time_ms"].mean(),
            "errors": w["is_error"].sum(),
            "warns": w["is_warn"].sum(),
            "label": label
        })

        t += pd.Timedelta(seconds=WINDOW_SEC)

    return pd.DataFrame(feats)


if __name__ == "__main__":
    print("📥 Loading logs...")
    df = load_logs()

    df = preprocess(df)

    print("🧮 Creating window features...")
    f = window_features(df)

    f.to_csv(OUT_FILE, index=False)

    print("✅ Saved features to", OUT_FILE)
