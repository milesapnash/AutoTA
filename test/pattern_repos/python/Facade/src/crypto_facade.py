from encryptor import Encryptor
from key_deriver import KeyDeriver
from signer import Signer


class CryptoFacade:
    def __init__(self):
        self._key_deriver = KeyDeriver()
        self._encryptor = Encryptor()
        self._signer = Signer()

    def protect(self, text, password):
        key = self._key_deriver.derive(password)
        encrypted = self._encryptor.encrypt(text, key)
        return self._signer.sign(encrypted, key)
