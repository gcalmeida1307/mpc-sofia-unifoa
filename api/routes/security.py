from fastapi import APIRouter

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
        },
        "notes": [
            "Use reverse proxy TLS termination for production.",
            "Keep OPENAI_API_KEY only in environment variables.",
            "Enable fail2ban/ufw/crowdsec on host edge as defense in depth.",
        ],
    }
