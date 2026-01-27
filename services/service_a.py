import time, random
from logger_utils import log_event
from metrics import get_metrics
from state_reader import get_failure_mode

SERVICE = "service_a"

def handle_request():
    mode = get_failure_mode()

    base = random.randint(40, 90)
    rt = base
    lvl = "INFO"
    evt = "request_ok"

    if mode == "db_overload":
        time.sleep(0.7)
        rt += 600
        lvl = "ERROR"
        evt = "db_timeout"

    elif mode == "network_delay":
        time.sleep(1)
        rt += 800
        lvl = "ERROR"
        evt = "net_timeout"

    m = get_metrics()

    log_event({
        "service": SERVICE,
        "level": lvl,
        "event": evt,
        "response_time_ms": rt,
        **m,
        "failure_mode": mode
    })

while True:
    handle_request()
