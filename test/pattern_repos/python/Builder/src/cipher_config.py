class CipherConfig:
    def __init__(self):
        self._algorithm = None
        self._key_size = None
        self._mode = None

    def set_algorithm(self, algorithm):
        self._algorithm = algorithm

    def set_key_size(self, key_size):
        self._key_size = key_size

    def set_mode(self, mode):
        self._mode = mode

    def __str__(self):
        return f"{self._algorithm}-{self._key_size}-{self._mode}"
