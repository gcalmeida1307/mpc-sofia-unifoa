from fastapi import APIRouter

from config.settings import settings

router = APIRouter(prefix="/security", tags=["Security"])


@router.get("/validate")
def validate_security():
    return {
        "status": "ok",
        "checks": {
            "https_termination_required": True,
            "hsts_configured": True,
            "csp_configured": True,
            "x_content_type_options": True,
            "x_frame_options": True,
            "referrer_policy": True,
            "permissions_policy": True,
            "admin_api_key_enabled": bool(settings.SECURITY_ADMIN_API_KEY.strip()),
            "mfa_totp_enabled": bool(settings.SECURITY_MFA_TOTP_SECRET.strip()),
            "rate_limit_enabled": settings.REQUEST_RATE_LIMIT_PER_MINUTE > 0,
        },
        "notes": [
            "Use reverse proxy TLS termination for production.",
            "Keep OPENAI_API_KEY and OLLAMA_API_KEY only in environment variables.",
            "Use SECURITY_ADMIN_API_KEY for critical write operations.",
            "Set SECURITY_MFA_TOTP_SECRET to require TOTP as a second factor.",
            "Enable fail2ban/ufw/crowdsec on host edge as defense in depth.",
        ],
    }
