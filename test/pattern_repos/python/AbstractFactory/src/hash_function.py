from abc import ABC, abstractmethod


class Hash(ABC):
    @abstractmethod
    def digest(self, message):
        pass
