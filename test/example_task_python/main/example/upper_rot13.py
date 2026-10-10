from main.example.cryptosystem import Cryptosystem


class UpperROT13(Cryptosystem):
    def transform_input(self):
        self._text = self._text.upper()

    def apply_cipher(self):
        self._text = self.shift_string(13)
