import logging
import random
from typing import override

from typing_extensions import TypedDict

from components.sensor import Sensor, SensorConfig


class RandomSensorConfig(SensorConfig):
    minimum: int = 10
    maximum: int = 20


class RandomSensor(Sensor):
    def __init__(self, config: RandomSensorConfig):
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.config: RandomSensorConfig = config
        super().__init__(config)

        if not self.enabled:
            return

        self.logger.info(
            f"RandomSensor: Min and max are {self.config.minimum} and {self.config.maximum}"
        )

    @override
    def read(self):
        if self.enabled:
            return {
                "a": random.randint(self.config.minimum, self.config.maximum),
                "b": random.randint(self.config.minimum, self.config.maximum),
                "c": random.randint(self.config.minimum, self.config.maximum),
            }


class PluginData(TypedDict):
    name: str
    desc: str
    impl: type[object]
    conf: type[object]
    type: str


SIGHTSPluginData: PluginData = {
    "name": "random_sensor",
    "desc": "Random Sensor",
    "type": "sensor",
    "impl": RandomSensor,
    "conf": RandomSensorConfig,
}
