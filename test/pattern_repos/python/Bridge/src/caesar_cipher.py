from cipher import Cipher


class CaesarCipher(Cipher):
    def apply(self, data):
        return f"Caesar({data})"
