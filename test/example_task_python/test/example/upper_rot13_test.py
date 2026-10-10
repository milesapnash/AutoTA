import unittest

from main.example.upper_rot13 import UpperROT13


class UpperROT13Test(unittest.TestCase):
    def test_encrypts_upper_case(self):
        self.assertEqual(UpperROT13().encrypt_string('HELLO'), 'URYYB')

    def test_encrypts_lower_case(self):
        self.assertEqual(UpperROT13().encrypt_string('hello'), 'URYYB')
