from .base_module import BaseModule
from .event_bus import event_bus
from .registry import registry

__all__ = ["Application", "BaseModule", "event_bus", "registry"]


def __getattr__(name):
    if name == "Application":
        from .application import Application
        return Application
    raise AttributeError(name)
