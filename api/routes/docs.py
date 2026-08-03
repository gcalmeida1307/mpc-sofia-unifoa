from fastapi import APIRouter

router = APIRouter(prefix="/docs", tags=["Docs"])


@router.post("/reindex")
def reindex_docs():
    return {
        "status": "queued",
        "engine": "Knowledge Engine",
        "message": "Reindexação solicitada. O diretório docs será consultado pelo Knowledge Service.",
    }
