import time, random
from logger_utils import log_event
from metrics import get_metrics
from state_reader import get_failure_mode

SERVICE = "service_c"

def handle_request():
    mode = get_failure_mode()

    base = random.randint(20, 60)
    rt = base
    lvl = "INFO"
    evt = "auth_ok"

    if mode == "network_delay":
        time.sleep(1)
        rt += 900
        lvl = "ERROR"
        evt = "net_timeout"

    elif mode == "cpu_spike":
        for _ in range(3_000_000):
            pass
        rt += 300
        lvl = "WARN"
        evt = "cpu_hot"

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
