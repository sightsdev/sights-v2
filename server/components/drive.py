from abc import ABC, abstractmethod

from pydantic.main import BaseModel


class DriveConfig(BaseModel):
    enabled: bool


class Drive(ABC):
    def __init__(self, config: DriveConfig):
        pass

    @abstractmethod
    def move_motor(self, channel: int, speed: int) -> None:
        pass

    @abstractmethod
    def move(self, speed: list[int | None]) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass
