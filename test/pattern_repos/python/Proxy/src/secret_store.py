from abc import ABC, abstractmethod


class SecretStore(ABC):
    @abstractmethod
    def read(self, secret_id):
        pass
