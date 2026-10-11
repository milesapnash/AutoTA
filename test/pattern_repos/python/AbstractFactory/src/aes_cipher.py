from cipher import Cipher


class AesCipher(Cipher):
    def encrypt(self, plaintext):
        return f"AES({plaintext})"
