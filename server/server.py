import logging
from pathlib import Path
from time import time
from typing import cast

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from starlette.types import ASGIApp

from components.camera import CameraComponent
from components.sensor import SensorConfig
from util.configs import LOG_FILE, ConfigManager
from util.helpers import SinglePageApplication
from util.logging import setup_logging
from util.state import State, load_state

# Init

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(debug=False)
app.state.data = load_state()


def get_state() -> State:
    return cast(State, app.state.data)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = FastAPI()

config_manager = ConfigManager()

# Frontend
app.mount("/api/camera/{id:str}", cast(ASGIApp, CameraComponent.stream))
app.mount("/api", api, name="api")
app.mount("/", SinglePageApplication(directory="../client/build"), name="frontend")

# Pydantic Classes


class MoveMotorsParams(BaseModel):
    speed: list[int]


class MoveArmServoParams(BaseModel):
    direction: bool
    amount: float = 1.8


class SwitchConfigBody(BaseModel):
    file: str = Field(..., pattern=r"^[^/\\\.]+\.toml$")


class UpdateConfigBody(BaseModel):
    content: str


VERSION_FILE = Path(__file__).parent / "VERSION"


@api.get("/version", response_class=PlainTextResponse)
async def get_version() -> str:
    """Get the current version."""
    try:
        return VERSION_FILE.read_text().strip()
    except FileNotFoundError:
        return "Unknown"
    except OSError as e:
        logger.error(f"Error reading version file: {e}")
        return "Unknown"


# Camera


@api.get("/camera/")
async def list_cameras() -> list[str]:
    """List all configured cameras."""
    return list(get_state().cameras.keys())


@api.get("/camera/all")
def list_available_cameras() -> list[int]:
    """List all avaliable cameras currently on the host system"""
    return CameraComponent.list_available()


# Drive


@api.post("/drive/")
async def drive(params: MoveMotorsParams) -> None:
    """Move drive motors at provided speed"""
    state = get_state()
    if state.drive is not None:
        state.drive.move(params.speed)
    else:
        logger.warning("Drive move was triggered, but there is no drive plugin")


@api.post("/drive/stop")
async def drive_stop() -> None:
    """Stop all drive motors."""
    state = get_state()
    if state.drive is not None:
        state.drive.stop()
    else:
        logger.warning("Drive stop was triggered, but there is no drive plugin")


# Sensors


@api.get("/sensor/list/")
async def sensor_list() -> dict[str, SensorConfig]:
    """List all available sensors and their configurations."""
    return {
        k: s.config
        for k, s in get_state().sensors.items()
        if isinstance(s.config, SensorConfig)
    }


@api.get("/sensor/{sensor_id}")
async def sensor_read(sensor_id: str):
    """Read data from a specific sensor."""
    state = get_state()
    if sensor_id not in state.sensors:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sensor with ID of {sensor_id} not found",
        )
    return state.sensors[sensor_id].read()


# Arm


@api.post("/arm/servo/{servo_name}")
async def arm_move(servo_name: str, params: MoveArmServoParams) -> None:
    """Move a specific servo on the arm."""
    state = get_state()
    if state.arm is not None:
        state.arm.increment_angle(servo_name, params.direction, params.amount)
    else:
        logger.warning("Arm movement was triggered, but there is no arm plugin")


@api.post("/arm/home")
async def arm_home() -> None:
    """Move arm to home position."""
    state = get_state()
    if state.arm is not None:
        await state.arm.home()
    else:
        logger.warning("Arm movement was triggered, but there is no arm plugin")


@api.post("/arm/preset/{preset}")
async def arm_preset(preset: str) -> None:
    """Move arm to a preset position."""
    state = get_state()
    if state.arm is not None:
        await state.arm.move_preset(preset)
    else:
        logger.warning("Arm movement was triggered, but there is no arm plugin")


# Host system


@api.post("/poweroff")
async def power() -> dict[str, str]:
    """Power off the system."""
    logger.info("Powering off...")
    # os.system('poweroff')
    return {"status": "powering off"}


@api.post("/reboot")
async def reboot() -> dict[str, str]:
    """Reboot the system."""
    logger.info("Rebooting...")
    # os.system('reboot')
    return {"status": "rebooting"}


@api.post("/reload")
def reload() -> dict[str, bool]:
    """Reload the application state from configuration."""
    state = get_state()
    if state.drive is not None:
        state.drive.close()
    app.state.data = load_state()
    return {"success": True}


@api.get("/logs", response_class=PlainTextResponse)
async def get_logs() -> str:
    """App log file"""
    try:
        return LOG_FILE.read_text()
    except FileNotFoundError:
        return "Log file not found"
    except OSError as e:
        return f"Error reading log file: {e}"


@api.get("/ping")
def ping_endpoint() -> dict[str, float]:
    """Returns the current network delay (aka ping)"""
    return {"timestamp": time() * 1000}


@api.post("/estop")
async def estop() -> dict[str, str]:
    """Emergency Stop - Use at own risk"""
    logger.info("Emergency stopping...")
    # os.system('poweroff -p -f')
    return {"status": "stopping"}


# Configuration


@api.get("/config/active")
async def get_active_config() -> dict[str, str]:
    """Get the currently active config file name."""
    return {"active_config_file": config_manager.get_active_config_name()}


@api.get("/config/list")
async def list_configs() -> dict[str, list[str]]:
    """List all available config files."""
    return {"configs": config_manager.list_config_files()}


@api.get("/config/file")
async def get_config_file() -> dict[str, str]:
    """Get the contents of the currently active config file."""
    config_path = config_manager.get_active_config_path()

    if not config_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config file not found: {config_path.name}",
        )

    try:
        return {"content": config_path.read_text(), "filename": config_path.name}
    except OSError as e:
        logger.error(f"Error reading config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading config file: {e}",
        )


@api.get("/config/backups")
async def list_backups() -> (
    dict[str, str | None] | dict[str, list[dict[str, str | int]] | str]
):
    """List all backup files for the currently active config."""
    return config_manager.list_backups()


@api.get("/config/backup/{filename}")
async def get_backup_file(filename: str) -> dict[str, str]:
    """Get the contents of a specific backup file."""
    return config_manager.get_backup_content(filename)


@api.post("/config/switch")
def switch_config(body: SwitchConfigBody) -> dict[str, bool]:
    """Switch to a different configuration file."""
    config_manager.switch_config(body.file)
    _ = reload()
    return {"success": True}


@api.post("/config/update")
def update_config(body: UpdateConfigBody) -> dict[str, bool]:
    """Update the current configuration file."""
    config_manager.update_config(body.content)
    _ = reload()
    return {"success": True}
