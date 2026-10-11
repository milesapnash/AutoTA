import base64

from encryptor_decorator import EncryptorDecorator


class Base64Decorator(EncryptorDecorator):
    def encrypt(self, text):
        encrypted = self._wrapped.encrypt(text)
        return base64.b64encode(encrypted.encode()).decode()
