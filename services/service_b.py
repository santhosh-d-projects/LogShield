import time, random
from logger_utils import log_event
from metrics import get_metrics
from state_reader import get_failure_mode

SERVICE = "service_b"

leak = []

def handle_request():
    mode = get_failure_mode()
    base = random.randint(30, 70)
    rt = base
    lvl = "INFO"
    evt = "query_ok"

    if mode == "cpu_spike":
        for _ in range(6_000_000):
            pass
        rt += 500
        lvl = "WARN"
        evt = "high_cpu"

    elif mode == "memory_leak":
        leak.append("x" * 10_000_00)
        rt += 200
        lvl = "WARN"
        evt = "mem_growth"

    elif mode == "db_overload":
        time.sleep(0.9)
        rt += 700
        lvl = "ERROR"
        evt = "slow_query"

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
