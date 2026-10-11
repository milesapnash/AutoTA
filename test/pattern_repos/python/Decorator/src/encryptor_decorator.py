from abc import ABC

from encryptor import Encryptor


class EncryptorDecorator(Encryptor, ABC):
    def __init__(self, wrapped: Encryptor):
        self._wrapped = wrapped
