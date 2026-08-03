from __future__ import annotations


class BaseModule:
    name: str = ""
    capabilities: list[str] | None = None

    def __init__(self):
        self.capabilities = list(self.capabilities or [])

    @classmethod
    def module_name(cls) -> str:
        return cls.name or cls.__name__.lower()
