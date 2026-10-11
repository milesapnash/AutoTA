from abc import ABC, abstractmethod

from cipher import Cipher


class Messenger(ABC):
    def send(self, message):
        cipher = self.create_cipher()
        return cipher.encrypt(message)

    @abstractmethod
    def create_cipher(self) -> Cipher:
        pass
