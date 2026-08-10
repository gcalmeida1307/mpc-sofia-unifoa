from core.domain_registry import DomainDefinition, DomainManifest, DomainMcpTool, DomainRoute


def _hello(_arguments):
    return {"domain": "demo", "message": "Olá do domínio instalado dinamicamente"}


def _routers():
    from .routes import router
    return [router]


def _mcp_tools():
    return [DomainMcpTool(
        name="sofia.demo.hello",
        description="Prove that an independently installed domain can publish an MCP tool.",
        input_schema={"type": "object", "properties": {}, "additionalProperties": False},
        handler=_hello,
        required_capability="demo.read",
    )]


domain = DomainDefinition(
    manifest=DomainManifest(
        domain_id="demo",
        version="1.0.0",
        display_name="Demonstração",
        description="Domínio mínimo usado para validar o contrato de instalação.",
    ),
    permissions=("demo.read",),
    routes=(DomainRoute("/demo", "demo.read"),),
    role_grants={"viewer": {"demo.read"}, "user": {"demo.read"}, "analyst": {"demo.read"}, "operator": {"demo.read"}},
    mcp_tools=_mcp_tools,
    routers=_routers,
    navigation=({"label": "Demo", "href": "/demo/hello", "capability": "demo.read"},),
)
