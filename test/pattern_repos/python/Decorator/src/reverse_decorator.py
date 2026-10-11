from encryptor_decorator import EncryptorDecorator


class ReverseDecorator(EncryptorDecorator):
    def encrypt(self, text):
        encrypted = self._wrapped.encrypt(text)
        return encrypted[::-1]
