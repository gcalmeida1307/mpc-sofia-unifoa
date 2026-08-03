from dotenv import load_dotenv
import os

load_dotenv()

class Settings:

   ZABBIX_URL= os.getenv("ZABBIX_URL")
   ZABBIX_USER= os.getenv("ZABBIX_USER")
   ZABBIX_PASSWORD= os.getenv("ZABBIX_PASSWORD")
   REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))
   POSTGRES_DSN = os.getenv("POSTGRES_DSN", "postgresql://sofia:sofia123@sofia_postgres:5432/sofia")
   QDRANT_URL = os.getenv("QDRANT_URL", "http://sofia_qdrant:6333")
   QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "sofia_memory")
   N8N_BASE_URL = os.getenv("N8N_BASE_URL", "http://sofia_n8n:5678")
   N8N_DEFAULT_WEBHOOK = os.getenv("N8N_DEFAULT_WEBHOOK", "sofia-investigation")
   OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
   OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")

settings = Settings()
