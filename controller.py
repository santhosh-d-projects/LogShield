import json, time, random
from datetime import datetime, UTC

import os

STATE_FILE = "state/failure_state.json"

os.makedirs("state", exist_ok=True)

MODES = [
    "normal",
    "cpu_spike",
    "memory_leak",
    "db_overload",
    "network_delay"
]

while True:
    m = random.choice(MODES)

    data = {
        "mode": m,
        "since": datetime.now(UTC).isoformat()

    }

    with open(STATE_FILE, "w") as f:
        json.dump(data, f)

    print("🔥 Injected failure:", m)
    time.sleep(15)
