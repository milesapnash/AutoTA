from abc import ABC, abstractmethod


# Abstract class defining Template Method
class Cryptosystem(ABC):
    # Template Method
    def encrypt_string(self, text):
        self._text = text
        self.transform_input()
        self.apply_cipher()
        return self._text

    # Hook Method
    def shift_string(self, shift):
        shift = shift % 26
        cipher_text = ''
        for c in self._text:
            if c.isalpha():
                base = ord('a') if c.islower() else ord('A')
                cipher_text += chr((ord(c) - base + shift) % 26 + base)
            else:
                cipher_text += c
        return cipher_text

    # Operations to be Implemented by Subclasses
    @abstractmethod
    def transform_input(self):
        pass

    @abstractmethod
    def apply_cipher(self):
        pass
