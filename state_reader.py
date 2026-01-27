import json

STATE_FILE = "state/failure_state.json"

def get_failure_mode():
    try:
        with open(STATE_FILE) as f:
            return json.load(f).get("mode", "normal")
    except:
        return "normal"
