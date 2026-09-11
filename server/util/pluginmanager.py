import importlib.util
import logging
import os
import sys
from collections.abc import Callable
from importlib.machinery import ModuleSpec
from pathlib import Path
from types import ModuleType
from typing import Literal, TypedDict, cast

logger = logging.getLogger("plugin")

SingleComponentType = Literal["arm", "drive"]
PluginType = Literal[SingleComponentType, "sensor"]


class SIGHTSPluginDataStructure(TypedDict):
    name: str
    desc: str
    impl: Callable[..., object]
    conf: Callable[..., object]
    type: PluginType


class NestedTypes(TypedDict):
    plugin: Callable[..., object] | None
    config: Callable[..., object] | None


class ImplementationTypes(TypedDict):
    arm: NestedTypes
    drive: NestedTypes
    sensor: dict[str, NestedTypes]


class PluginManager:
    def __init__(self):
        self.plugins_dir: Path = Path("./plugins")
        self.current_dir: Path = Path(__file__).parents[1]
        self.implementations: ImplementationTypes = {
            "arm": {
                "plugin": None,
                "config": None,
            },
            "drive": {
                "plugin": None,
                "config": None,
            },
            "sensor": {},
        }

    def find_plugins(self):
        found_plugins: list[str] = []

        for file_path in self.plugins_dir.glob("*.py"):
            if not file_path.name.startswith("_"):
                found_plugins.append(str(file_path))

        for dir_path in self.plugins_dir.iterdir():
            if dir_path.is_dir() and not dir_path.name.startswith("_"):
                for file_path in dir_path.glob("*.py"):
                    if not file_path.name.startswith("_"):
                        found_plugins.append(str(file_path))
                for dir in dir_path.iterdir():
                    if dir.name == "_libraries":
                        sys.path.append(os.path.join(dir))

        return found_plugins

    def import_plugin(self, path: str):
        name = os.path.basename(path)
        absolute_path = (self.current_dir / path).resolve()
        spec: ModuleSpec | None = importlib.util.spec_from_file_location(
            name, absolute_path
        )
        if spec is None or spec.loader is None:
            raise ImportError(
                f"Failed to import plugin: Could not load spec for {absolute_path}"
            )
        plugin: ModuleType = importlib.util.module_from_spec(spec)
        sys.modules[path] = plugin
        spec.loader.exec_module(plugin)

        try:
            plugin_data = cast(SIGHTSPluginDataStructure, plugin.SIGHTSPluginData)
            plugin_type = plugin_data["type"]
            plugin_name = plugin_data["name"]
        except AttributeError as _:
            logger.error(f"{plugin.__name__} has no SIGHTSPluginData, cannot import")
            return

        target: NestedTypes | None = None

        if plugin_type == "sensor":
            sensor_dict = self.implementations["sensor"]
            if plugin_name not in sensor_dict:
                sensor_dict[plugin_name] = {"plugin": None, "config": None}
            target = sensor_dict[plugin_name]

        elif plugin_type in ("arm", "drive"):
            target = self.implementations[plugin_type]

        if target is not None:
            if target["plugin"] is None and target["config"] is None:
                target["plugin"] = plugin_data["impl"]
                target["config"] = plugin_data["conf"]
                logger.info(f"Imported {plugin_name} of type '{plugin_type}'")
            else:
                logger.info(f"Imported {plugin_name}")
                logger.warning(
                    f"Not set {plugin_name} as {plugin_type} implementation, as there is already one present"
                )
