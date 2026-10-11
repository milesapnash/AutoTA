from cipher import Cipher


class DesCipher(Cipher):
    def encrypt(self, plaintext):
        return f"DES({plaintext})"
