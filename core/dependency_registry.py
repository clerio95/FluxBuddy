"""Central dependency container for shared services."""


class DependencyRegistry:
    """Simple service locator — modules receive dependencies from here."""

    def __init__(self):
        self._services: dict[str, object] = {}

    def register(self, name: str, service: object) -> None:
        self._services[name] = service

    def get(self, name: str) -> object:
        if name not in self._services:
            raise KeyError(f"Dependency '{name}' not registered")
        return self._services[name]

    def has(self, name: str) -> bool:
        return name in self._services

    @property
    def registered(self) -> list[str]:
        return list(self._services.keys())
