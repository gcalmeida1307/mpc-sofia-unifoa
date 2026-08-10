from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


class UnsafeURL(ValueError):
    pass


def _is_forbidden(address: str) -> bool:
    ip = ipaddress.ip_address(address)
    return any((ip.is_private, ip.is_loopback, ip.is_link_local, ip.is_multicast, ip.is_reserved, ip.is_unspecified))


def validate_external_url(url: str, allowed_hosts: set[str] | None = None) -> str:
    parsed = urlparse(str(url).strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise UnsafeURL("A fonte deve usar uma URL HTTP ou HTTPS válida")
    if parsed.username or parsed.password:
        raise UnsafeURL("Credenciais não podem ser incluídas na URL")
    host = parsed.hostname.rstrip(".").lower()
    if allowed_hosts and host not in {item.rstrip('.').lower() for item in allowed_hosts}:
        raise UnsafeURL("O domínio não está na lista permitida para esta fonte")
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)}
    except socket.gaierror as exc:
        raise UnsafeURL("Não foi possível resolver o domínio da fonte") from exc
    if not addresses or any(_is_forbidden(address) for address in addresses):
        raise UnsafeURL("A URL aponta para uma rede interna, local ou reservada")
    return parsed.geturl()
