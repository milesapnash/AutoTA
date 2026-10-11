from cipher_config import CipherConfig
from config_builder import ConfigBuilder


class SecureConfigBuilder(ConfigBuilder):
    def __init__(self):
        self._config = CipherConfig()

    def build_algorithm(self):
        self._config.set_algorithm("AES")

    def build_key_size(self):
        self._config.set_key_size(256)

    def build_mode(self):
        self._config.set_mode("GCM")

    def get_result(self):
        return self._config
