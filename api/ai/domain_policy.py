from __future__ import annotations

import re
import unicodedata

OUT_OF_SCOPE_MESSAGE = (
    "Assunto fora da base de pesquisa. A SOFIA responde somente sobre informática, "
    "incluindo redes de computadores, sistemas operacionais, bancos de dados, normas "
    "de informática, aprendizado de máquina e inteligência artificial. Solicite ao "
    "administrador a inclusão de uma base de conhecimento adequada."
)

IT_TERMS = {
    "informatica", "computador", "computacao", "hardware", "software", "servidor", "cliente",
    "rede", "redes", "switch", "roteador", "router", "firewall", "vlan", "vpn", "dns", "dhcp",
    "tcp", "udp", "ip", "ipv4", "ipv6", "ethernet", "wifi", "wi-fi", "latencia", "pacote",
    "linux", "windows", "unix", "ubuntu", "debian", "kernel", "processo", "memoria", "cpu", "disco",
    "docker", "container", "kubernetes", "virtualizacao", "vmware", "proxmox", "cloud", "nuvem",
    "banco", "dados", "database", "sql", "postgresql", "postgres", "mysql", "oracle", "mongodb", "redis",
    "programacao", "codigo", "api", "python", "javascript", "java", "git", "github", "devops", "ci", "cd",
    "seguranca", "ciberseguranca", "criptografia", "senha", "autenticacao", "totp", "malware", "vulnerabilidade",
    "zabbix", "grafana", "prometheus", "loki", "observabilidade", "metrica", "log", "logs", "trace", "alerta",
    "mcp", "rag", "llm", "claude", "openai", "ollama", "ia", "inteligencia", "artificial", "machine",
    "learning", "aprendizado", "modelo", "neural", "algoritmo", "automacao", "workflow", "n8n",
    "iso27001", "iso", "cobit", "itil", "lgpd", "governanca", "backup", "restore", "jira",
}
GREETING_PATTERNS = (r"^(oi|ola|bom dia|boa tarde|boa noite)\b", r"^(ajuda|help)\b")


def normalize(text: str) -> str:
    value = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in value if not unicodedata.combining(char))


def is_it_question(question: str) -> bool:
    normalized = normalize(question)
    if any(re.search(pattern, normalized) for pattern in GREETING_PATTERNS):
        return True
    tokens = set(re.findall(r"[a-z0-9+#.-]+", normalized))
    if tokens.intersection(IT_TERMS):
        return True
    return any(phrase in normalized for phrase in ("sistema operacional", "banco de dados", "rede de computadores", "inteligencia artificial", "aprendizado de maquina"))
