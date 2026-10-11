from abc import ABC, abstractmethod


class Key(ABC):
    @abstractmethod
    def copy(self) -> "Key":
        pass
