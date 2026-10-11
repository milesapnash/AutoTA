from abc import ABC, abstractmethod

from cipher_config import CipherConfig


class ConfigBuilder(ABC):
    @abstractmethod
    def build_algorithm(self):
        pass

    @abstractmethod
    def build_key_size(self):
        pass

    @abstractmethod
    def build_mode(self):
        pass

    @abstractmethod
    def get_result(self) -> CipherConfig:
        pass
