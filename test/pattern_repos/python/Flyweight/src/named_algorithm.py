from cipher_algorithm import CipherAlgorithm


class NamedAlgorithm(CipherAlgorithm):
    def __init__(self, name):
        self._name = name

    def encrypt(self, text, key):
        return f"{self._name}({text},{key})"
