from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, Gauge, generate_latest
from services.infrastructure import get_server_resources

router=APIRouter(tags=["Metrics"])
CPU=Gauge("sofia_server_cpu_load_percent","Estimated server CPU load percentage")
MEMORY=Gauge("sofia_server_memory_used_percent","Server memory used percentage")
DISK=Gauge("sofia_server_disk_used_percent","Server disk used percentage")
DB_SIZE=Gauge("sofia_postgres_database_size_bytes","SOFIA PostgreSQL database size")

@router.get("/metrics",include_in_schema=False)
def metrics():
    data=get_server_resources(); CPU.set(data.get("cpu",{}).get("load_percent_estimate",0)); MEMORY.set(data.get("memory",{}).get("used_percent",0)); DISK.set(data.get("disk",{}).get("used_percent",0)); DB_SIZE.set(float(data.get("database",{}).get("size_mb",0) or 0)*1024*1024)
    return Response(generate_latest(),media_type=CONTENT_TYPE_LATEST)
