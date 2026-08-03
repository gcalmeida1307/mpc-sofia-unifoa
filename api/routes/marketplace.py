from fastapi import APIRouter
from pydantic import BaseModel

from services.marketplace import get_marketplace_catalog, install_module

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])


class MarketplaceInstallRequest(BaseModel):
    module_name: str
    version: str | None = None


@router.get("/catalog")
def catalog():
    return get_marketplace_catalog()


@router.post("/install")
def install(payload: MarketplaceInstallRequest):
    return install_module(payload.module_name, payload.version)
