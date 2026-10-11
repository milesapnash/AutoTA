from abc import ABC, abstractmethod

from cipher import Cipher
from hash_function import Hash


class CryptoFactory(ABC):
    @abstractmethod
    def create_cipher(self) -> Cipher:
        pass

    @abstractmethod
    def create_hash(self) -> Hash:
        pass
