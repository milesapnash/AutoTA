from cipher import Cipher


class XorCipher(Cipher):
    def apply(self, data):
        return f"XOR({data})"
