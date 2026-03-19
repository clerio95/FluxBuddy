"""Dynamic module discovery and loading from the modules/ directory."""

from __future__ import annotations

import importlib
import json
import logging
import os
from pathlib import Path
from typing import Any

from core.contracts import FluxModule, ModuleContext
from core.exceptions import ModuleLoadError
from core.types import ModuleManifest

MODULES_DIR = Path(__file__).resolve().parent.parent / "modules"


def _load_manifest(manifest_path: Path) -> ModuleManifest | None:
    """Parse and validate a plugin.json file."""
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return ModuleManifest(
            name=data["name"],
            version=data.get("version", "0.0.0"),
            enabled=data.get("enabled", True),
            entrypoint=data["entrypoint"],
        )
    except (json.JSONDecodeError, KeyError, OSError):
        return None


def load_modules(
    logger: logging.Logger,
    event_bus: Any,
    settings: Any,
    deps: Any,
) -> list[FluxModule]:
    """Scan modules/ for valid plugin.json files and load enabled modules."""
    modules: list[FluxModule] = []

    if not MODULES_DIR.is_dir():
        logger.warning(
            f"action=loader.skip | reason=modules_dir_missing | path={MODULES_DIR}"
        )
        return modules

    for child in sorted(MODULES_DIR.iterdir()):
        if not child.is_dir():
            continue
        manifest_path = child / "plugin.json"
        if not manifest_path.is_file():
            continue

        manifest = _load_manifest(manifest_path)
        if manifest is None:
            logger.error(f"action=module.manifest_invalid | path={manifest_path}")
            continue

        if not manifest.enabled:
            logger.info(
                f"action=module.skipped | module={manifest.name} | reason=disabled"
            )
            continue

        try:
            module_path, factory_name = manifest.entrypoint.rsplit(":", 1)
            mod_py = importlib.import_module(module_path)
            factory = getattr(mod_py, factory_name)

            ctx = ModuleContext(
                logger=logger,
                event_bus=event_bus,
                settings=settings,
                deps=deps,
                module_name=manifest.name,
            )
            instance = factory(ctx)

            if not isinstance(instance, FluxModule):
                raise ModuleLoadError("Factory did not return a FluxModule instance")

            modules.append(instance)
            logger.info(
                f"action=module.loaded | module={manifest.name} "
                f"| version={manifest.version} | commands={len(instance.commands)} "
                f"| jobs={len(instance.jobs)} | listeners={len(instance.event_listeners)}"
            )
        except Exception as exc:
            logger.error(
                f"action=module.load_failed | module={manifest.name} | error={exc}"
            )
            continue

    return modules
