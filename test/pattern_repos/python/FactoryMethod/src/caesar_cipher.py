from cipher import Cipher


class CaesarCipher(Cipher):
    def encrypt(self, plaintext):
        return f"Caesar({plaintext})"
