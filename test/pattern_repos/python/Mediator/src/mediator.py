from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from participant import Participant


class Mediator(ABC):
    @abstractmethod
    def relay(self, message, sender: "Participant"):
        pass
