from abc import ABC, abstractmethod


class CryptoStep(ABC):
    @abstractmethod
    def apply(self, text):
        pass
