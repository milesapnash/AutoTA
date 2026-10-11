from cipher import Cipher


class ReverseCipher(Cipher):
    def encrypt(self, plaintext):
        return plaintext[::-1]
