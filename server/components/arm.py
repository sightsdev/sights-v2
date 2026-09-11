from abc import ABC, abstractmethod

from pydantic import BaseModel


class ArmServoConfig(BaseModel):
    index: int
    range_min: int
    range_max: int
    home: int
    presets: dict[str, int] | None = None


class ArmConfig(BaseModel):
    enabled: bool = True
    servos: dict[str, ArmServoConfig]


class Arm(ABC):
    def __init__(self, config: ArmConfig):
        pass

    @abstractmethod
    async def home(self):
        pass

    @abstractmethod
    async def move_preset(self, preset_name: str):
        pass

    @abstractmethod
    def increment_angle(self, joint: str, direction: bool, amount: float = 180 / 100):
        pass

    @abstractmethod
    def close(self) -> None:
        pass
