from fastapi import APIRouter
from connectors.zabbix import ZabbixConnector

router = APIRouter(prefix="/zabbix", tags=["Zabbix"])

@router.get("/login")
def login():

    connector = ZabbixConnector()
    token = connector.login()

    return {
        "status": "Autenticado",
        "token": token
    }
