import unittest

from core.registry import registry
from core.base_module import BaseModule


class DummyModule(BaseModule):
    name = "dummy"


class RegistryTestCase(unittest.TestCase):
    def test_registry_registers_modules(self):
        registry.clear()
        registry.register(DummyModule)

        self.assertIn("dummy", registry.list_modules())

    def test_registry_exposes_capabilities(self):
        registry.clear()
        registry.register(DummyModule)
        registry.register_capability("dummy", "ping")

        self.assertIn("ping", registry.get_capabilities("dummy"))


if __name__ == "__main__":
    unittest.main()
