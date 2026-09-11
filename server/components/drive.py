from abc import ABC, abstractmethod


class Drive(ABC):
    @abstractmethod
    def move_motor(self, channel: int, speed: int) -> None:
        pass

    @abstractmethod
    def move(self, speed: list[int]) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass
