from abc import ABC, abstractmethod

from pydantic import BaseModel


class SensorConfig(BaseModel):
    enabled: bool = False
    mock: bool = False


class Sensor(ABC):
    def __init__(self, config: SensorConfig):
        self.config: SensorConfig = config
        self.enabled: bool = config.enabled
        self.mock: bool = config.mock

    @abstractmethod
    def read(self) -> dict[str, int] | None:
        pass
