import unittest

from main.example.caesar_cipher import CaesarCipher


class CaesarCipherTest(unittest.TestCase):
    # Intentionally not in snake case for testing
    def testShiftZeroIsSelf(self):
        cryptosystem = CaesarCipher(0)
        self.assertEqual(cryptosystem.encrypt_string('Hello'), 'Hello')

    # Intentionally not in snake case for testing
    def testShiftOne(self):
        cryptosystem = CaesarCipher(1)
        self.assertEqual(cryptosystem.encrypt_string('Hello'), 'Ifmmp')
