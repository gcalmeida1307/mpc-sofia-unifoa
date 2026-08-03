from core.registry import registry


def get_mcp_tools():
    snapshot = registry.get_snapshot()
    return {
        "provider": "SOFIA MCP",
        "modules": snapshot["modules"],
        "capabilities": snapshot["capabilities"],
    }
