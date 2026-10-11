from abc import ABC, abstractmethod

from cipher import Cipher


class SecureChannel(ABC):
    def __init__(self, cipher: Cipher):
        self._cipher = cipher

    @abstractmethod
    def transmit(self, data):
        pass
