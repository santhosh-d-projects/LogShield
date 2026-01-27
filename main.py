import subprocess
import sys
import time

processes = []

def start(cmd):
    print("▶ Starting:", " ".join(cmd))
    p = subprocess.Popen(cmd)
    processes.append(p)

try:
    # Start controller
    start([sys.executable, "controller.py"])
    time.sleep(2)

    # Start services
    start([sys.executable, "-m", "services.service_a"])
    start([sys.executable, "-m", "services.service_b"])
    start([sys.executable, "-m", "services.service_c"])

    print("\n🔥 All components running!")
    print("Press CTRL+C to stop everything.\n")

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n🛑 Shutting down all processes...")

    for p in processes:
        p.terminate()

    print("✅ Done.")
