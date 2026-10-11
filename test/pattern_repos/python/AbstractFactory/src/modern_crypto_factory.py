from aes_cipher import AesCipher
from crypto_factory import CryptoFactory
from sha256_hash import Sha256Hash


class ModernCryptoFactory(CryptoFactory):
    def create_cipher(self):
        return AesCipher()

    def create_hash(self):
        return Sha256Hash()
