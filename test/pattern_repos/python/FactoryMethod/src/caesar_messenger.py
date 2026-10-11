from caesar_cipher import CaesarCipher
from messenger import Messenger


class CaesarMessenger(Messenger):
    def create_cipher(self):
        return CaesarCipher()
