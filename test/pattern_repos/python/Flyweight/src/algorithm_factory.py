from cipher_algorithm import CipherAlgorithm
from named_algorithm import NamedAlgorithm


class AlgorithmFactory:
    def __init__(self):
        self._pool: dict[str, CipherAlgorithm] = {}

    def get(self, name) -> CipherAlgorithm:
        if name not in self._pool:
            self._pool[name] = NamedAlgorithm(name)
        return self._pool[name]
