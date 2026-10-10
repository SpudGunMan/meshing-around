"""Discover paired .py/.toml plugins; rejected plugins never gain registrations."""

import importlib.util
import logging
import re
import sys
import tomllib

from . import API_VERSION

log = logging.getLogger(__name__)


async def load_plugins(runtime, directory):
    report = {}
    stems = sorted({p.stem for p in directory.iterdir() if p.suffix in (".py", ".toml")})
    for name in stems:
        module_name = f"bot_plugin_{name}"
        try:
            if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
                raise ValueError("invalid plugin filename")
            config_path, source = directory / f"{name}.toml", directory / f"{name}.py"
            if not config_path.is_file() or not source.is_file():
                raise ValueError("plugin needs both .py and .toml files")
            if config_path.is_symlink() or source.is_symlink():
                raise ValueError("plugin files must not be symlinks")
            with config_path.open("rb") as stream:
                config = tomllib.load(stream)
            metadata = config.get("plugin", {})
            if not isinstance(metadata.get("enabled"), bool):
                raise ValueError("plugin.enabled must be a boolean")
            if not metadata["enabled"]:
                report[name] = {"status": "disabled"}
                continue
            if metadata.get("id") != name:
                raise ValueError("plugin.id must match filename")
            if type(metadata.get("api_version")) is not int or metadata["api_version"] != API_VERSION:
                raise ValueError(f"plugin requires core api_version={API_VERSION}")
            if not isinstance(metadata.get("version"), str) or not metadata["version"]:
                raise ValueError("plugin.version is required")
            settings = config.get("settings", {})
            if not isinstance(settings, dict):
                raise ValueError("settings must be a TOML table")
            spec = importlib.util.spec_from_file_location(module_name, source)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            registration = module.register(settings)
            await runtime.activate(name, registration)
            report[name] = {"status": "active", "version": metadata["version"]}
        except (Exception, SystemExit) as error:
            sys.modules.pop(module_name, None)
            report[name] = {"status": "rejected", "reason": str(error)}
            log.warning("Skipping plugin %s: %s", name, error)
    return report
