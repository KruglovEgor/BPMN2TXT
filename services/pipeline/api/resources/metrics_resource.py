import os
import platform
import time
import psutil
from starlette.responses import JSONResponse


_process = psutil.Process(os.getpid())


def get_metrics():
    """Возвращает метрики использования ресурсов контейнера."""
    psutil.cpu_percent(interval=None)
    _process.cpu_percent(interval=None)
    time.sleep(0.1)
    cpu_percent = psutil.cpu_percent(interval=None)
    cpu_count = psutil.cpu_count(logical=True) or 0

    memory = psutil.virtual_memory()
    process_memory = _process.memory_info()
    process_cpu_percent = _process.cpu_percent(interval=None)

    disk_path = os.getenv("METRICS_DISK_PATH", "/")
    disk_usage = psutil.disk_usage(disk_path)

    payload = {
        "system": {
            "platform": platform.system(),
            "cpu_percent": cpu_percent,
            "cpu_count": cpu_count,
            "memory_total_bytes": memory.total,
            "memory_used_bytes": memory.used,
            "memory_available_bytes": memory.available,
            "memory_percent": memory.percent,
            "disk_total_bytes": disk_usage.total,
            "disk_used_bytes": disk_usage.used,
            "disk_free_bytes": disk_usage.free,
            "disk_percent": disk_usage.percent,
        },
        "process": {
            "pid": _process.pid,
            "cpu_percent": process_cpu_percent,
            "memory_rss_bytes": process_memory.rss,
            "memory_vms_bytes": process_memory.vms,
        }
    }

    return JSONResponse(content=payload, status_code=200)
