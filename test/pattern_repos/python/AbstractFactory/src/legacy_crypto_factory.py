from crypto_factory import CryptoFactory
from des_cipher import DesCipher
from md5_hash import Md5Hash


class LegacyCryptoFactory(CryptoFactory):
    def create_cipher(self):
        return DesCipher()

    def create_hash(self):
        return Md5Hash()
