from main.example.cryptosystem import Cryptosystem


class CaesarCipher(Cryptosystem):
    def __init__(self, shift):
        # Intentionally public for testing
        self.cipher_shift = shift

    def transform_input(self):
        pass

    def apply_cipher(self):
        self._text = self.shift_string(self.cipher_shift)
