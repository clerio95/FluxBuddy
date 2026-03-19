import json
import logging
from pathlib import Path

from core.contracts import FluxModule, ModuleContext
from core.plugin_loader import _load_manifest


class DummyModule(FluxModule):
    @property
    def name(self) -> str:
        return "dummy"


def test_load_manifest_valid(tmp_path: Path):
    manifest = tmp_path / "plugin.json"
    manifest.write_text(
        json.dumps(
            {
                "name": "dummy",
                "version": "0.1.0",
                "enabled": True,
                "entrypoint": "modules.dummy.module:create_module",
            }
        ),
        encoding="utf-8",
    )

    parsed = _load_manifest(manifest)

    assert parsed is not None
    assert parsed.name == "dummy"
    assert parsed.entrypoint == "modules.dummy.module:create_module"


def test_load_manifest_invalid(tmp_path: Path):
    manifest = tmp_path / "plugin.json"
    manifest.write_text('{"name": "dummy"}', encoding="utf-8")

    parsed = _load_manifest(manifest)

    assert parsed is None
