from cipher_config import CipherConfig
from config_builder import ConfigBuilder


class ConfigDirector:
    def __init__(self, builder: ConfigBuilder):
        self._builder = builder

    def construct(self) -> CipherConfig:
        self._builder.build_algorithm()
        self._builder.build_key_size()
        self._builder.build_mode()
        return self._builder.get_result()
