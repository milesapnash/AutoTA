from messenger import Messenger
from reverse_cipher import ReverseCipher


class ReverseMessenger(Messenger):
    def create_cipher(self):
        return ReverseCipher()
