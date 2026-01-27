import psutil

def get_metrics():
    return {
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().used // (1024*1024)
    }
