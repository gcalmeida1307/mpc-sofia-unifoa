from fastapi import APIRouter
from services.dashboard import dashboard_summary
router=APIRouter(prefix="/dashboard",tags=["Dashboard"])
@router.get("/summary")
def summary():
    return dashboard_summary()
