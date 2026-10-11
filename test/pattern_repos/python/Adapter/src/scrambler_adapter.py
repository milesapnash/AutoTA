from cipher import Cipher
from legacy_scrambler import LegacyScrambler


class ScramblerAdapter(Cipher):
    def __init__(self, scrambler: LegacyScrambler):
        self._scrambler = scrambler

    def encrypt(self, plaintext):
        return self._scrambler.scramble(plaintext, 3)
