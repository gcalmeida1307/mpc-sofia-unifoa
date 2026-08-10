from fastapi import APIRouter


router = APIRouter(prefix="/demo", tags=["Demo Domain"])


@router.get("/hello")
def hello():
    return {"domain": "demo", "message": "Olá do domínio instalado dinamicamente"}
