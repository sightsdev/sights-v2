import logging
import tomllib as toml
from typing import cast

from pydantic import BaseModel

from components.arm import Arm
from components.camera import CameraConfig, CameraParameters
from components.drive import Drive
from components.sensor import Sensor
from util.configs import ConfigManager
from util.pluginmanager import PluginManager
from util.sysinfo import SystemInfo, SystemInfoConfig


class State(BaseModel):
    cameras: dict[str, CameraParameters] = {}
    sensors: dict[str, Sensor | SystemInfo] = {}
    drive: Drive | None = None
    arm: Arm | None = None

    class Config:
        arbitrary_types_allowed: bool = True


logger = logging.getLogger("server")


def load_state() -> State:
    config_path = ConfigManager().get_active_config_path()
    with open(config_path, "rb") as f:
        config = cast(dict[str, dict[str, object]], toml.load(f))

    new_state = State()
    plugin_manager = PluginManager()

    # Cameras
    camera_cfg = CameraConfig.parse_obj(config["camera"])

    for label, index in camera_cfg.devices.items():
        new_state.cameras[label] = CameraParameters(
            id=label,
            width=camera_cfg.width,
            height=camera_cfg.height,
            framerate=camera_cfg.framerate,
            quality=camera_cfg.quality,
            source=index,
        )

    for path in plugin_manager.find_plugins():
        plugin_manager.import_plugin(path)

    # Drive
    if config["drive"]["enabled"]:
        drive_plugin = plugin_manager.implementations["drive"]["plugin"]
        if drive_plugin is not None:
            new_state.drive = cast(Drive, drive_plugin())
        else:
            logger.error("Drive is enabled, but there is no drive plugin present")

    # Arm
    if config["arm"]["enabled"]:
        arm_plugin = plugin_manager.implementations["arm"]["plugin"]
        arm_config_class = plugin_manager.implementations["arm"]["config"]
        if arm_plugin is not None and arm_config_class is not None:
            arm_config = arm_config_class(**config["arm"])
            new_state.arm = cast(Arm, arm_plugin(arm_config))
        else:
            logger.error("Arm is enabled, but there is no arm plugin present")

    # System Info
    sys_info_conf = SystemInfoConfig.parse_obj(config["interface"]["system_info"])
    new_state.sensors["system_info"] = SystemInfo(sys_info_conf)

    # Sensors
    sensors_cfg = cast(dict[str, dict[str, object]], config["sensors"])
    sensors: dict[str, Sensor] = {}

    for key, value in plugin_manager.implementations["sensor"].items():
        sensor_plugin = value["plugin"]
        sensor_config_cls = value["config"]
        sensor_data = sensors_cfg.get(key)

        if (
            sensor_plugin is not None
            and sensor_config_cls is not None
            and sensor_data is not None
        ):
            sensor_config = sensor_config_cls(**sensor_data)
            sensor = cast(Sensor, sensor_plugin(sensor_config))
            sensors[key] = sensor
            logger.info(f"Loaded sensor {key}")
        else:
            logger.error(
                f"Not loading sensor {key} as there are no config options set for it"
            )

    new_state.sensors.update(sensors)

    return new_state
