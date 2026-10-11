from abc import ABC, abstractmethod


class Cipher(ABC):
    @abstractmethod
    def apply(self, data):
        pass
