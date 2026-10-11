from abc import ABC, abstractmethod


class CipherAlgorithm(ABC):
    @abstractmethod
    def encrypt(self, text, key):
        pass
