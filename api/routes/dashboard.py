from fastapi import APIRouter
from services.dashboard import dashboard_summary
from services.executive_dashboard import executive_summary
router=APIRouter(prefix="/dashboard",tags=["Dashboard"])
@router.get("/summary")
def summary():
    return dashboard_summary()
@router.get("/executive")
def executive():
    return executive_summary()
