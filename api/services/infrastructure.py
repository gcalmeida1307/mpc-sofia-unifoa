from __future__ import annotations

import os
import shutil
from pathlib import Path


def _read_meminfo() -> dict[str, int]:
    data: dict[str, int] = {}
    meminfo = Path("/proc/meminfo")
    if not meminfo.exists():
        return data
    try:
        for line in meminfo.read_text(encoding="utf-8").splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            number = value.strip().split()[0]
            data[key] = int(number)
    except Exception:
        return {}
    return data


def _read_network_usage() -> dict[str, int]:
    proc_net = Path("/proc/net/dev")
    if not proc_net.exists():
        return {"interfaces": 0, "rx_bytes": 0, "tx_bytes": 0}
    interfaces = 0
    rx_bytes = 0
    tx_bytes = 0
    try:
        for line in proc_net.read_text(encoding="utf-8").splitlines()[2:]:
            if ":" not in line:
                continue
            iface, payload = line.split(":", 1)
            iface = iface.strip()
            if not iface or iface == "lo":
                continue
            fields = payload.split()
            if len(fields) < 16:
                continue
            interfaces += 1
            rx_bytes += int(fields[0])
            tx_bytes += int(fields[8])
    except Exception:
        return {"interfaces": 0, "rx_bytes": 0, "tx_bytes": 0}
    return {"interfaces": interfaces, "rx_bytes": rx_bytes, "tx_bytes": tx_bytes}


def _read_database_usage() -> dict[str, object]:
    try:
        from services.postgres_store import postgres_store

        with postgres_store._connect() as conn:  # noqa: SLF001 - local observability helper
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        current_database(),
                        pg_database_size(current_database())::bigint,
                        (SELECT COUNT(*)::int FROM pg_stat_activity WHERE datname = current_database()),
                        (SELECT COUNT(*)::int FROM pg_stat_activity WHERE datname = current_database() AND state = 'active')
                    """
                )
                database_name, size_bytes, connections, active_connections = cur.fetchone()
        return {
            "name": database_name,
            "size_gb": round(size_bytes / (1024**3), 2),
            "size_mb": round(size_bytes / (1024**2), 2),
            "connections": connections,
            "active_connections": active_connections,
        }
    except Exception as exc:
        return {"error": str(exc)}


def get_server_resources() -> dict[str, object]:
    disk = shutil.disk_usage("/")
    meminfo = _read_meminfo()
    total_mem_kb = meminfo.get("MemTotal", 0)
    available_mem_kb = meminfo.get("MemAvailable", meminfo.get("MemFree", 0))
    used_mem_kb = max(total_mem_kb - available_mem_kb, 0)
    cpu_cores = os.cpu_count() or 1
    try:
        load_avg = os.getloadavg()
    except Exception:
        load_avg = (0.0, 0.0, 0.0)
    network = _read_network_usage()
    database = _read_database_usage()
    return {
        "disk": {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "used_percent": round((disk.used / disk.total) * 100, 1) if disk.total else 0,
        },
        "memory": {
            "total_gb": round(total_mem_kb / (1024**2), 2),
            "used_gb": round(used_mem_kb / (1024**2), 2),
            "available_gb": round(available_mem_kb / (1024**2), 2),
            "used_percent": round((used_mem_kb / total_mem_kb) * 100, 1) if total_mem_kb else 0,
        },
        "cpu": {
            "cores": cpu_cores,
            "load_1m": round(load_avg[0], 2),
            "load_5m": round(load_avg[1], 2),
            "load_15m": round(load_avg[2], 2),
            "load_percent_estimate": round(min((load_avg[0] / cpu_cores) * 100, 999.9), 1) if cpu_cores else 0,
        },
        "network": {
            "interfaces": network["interfaces"],
            "rx_mb": round(network["rx_bytes"] / (1024**2), 2),
            "tx_mb": round(network["tx_bytes"] / (1024**2), 2),
        },
        "database": database,
    }


def get_infrastructure_summary():
    return {
        "ambiente": "Producao",
        "hosts": 0,
        "online": 0,
        "offline": 0,
        "problemas_criticos": 0,
        "resources": get_server_resources(),
    }
