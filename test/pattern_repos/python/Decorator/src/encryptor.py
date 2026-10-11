from abc import ABC, abstractmethod


class Encryptor(ABC):
    @abstractmethod
    def encrypt(self, text):
        pass
