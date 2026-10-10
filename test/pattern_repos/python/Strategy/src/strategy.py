from abc import ABC, abstractmethod


class Strategy(ABC):
    @abstractmethod
    def algorithm(self):
        pass
