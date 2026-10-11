from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from secure_connection import SecureConnection


class ConnectionState(ABC):
    @abstractmethod
    def send(self, connection: "SecureConnection", data):
        pass
