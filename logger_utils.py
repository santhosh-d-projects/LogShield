import json, os
from datetime import datetime

LOG_FILE = "logs/system_logs.jsonl"

os.makedirs("logs", exist_ok=True)

def log_event(data):
    data["timestamp"] = datetime.utcnow().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")
