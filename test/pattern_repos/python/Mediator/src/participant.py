from abc import ABC, abstractmethod

from mediator import Mediator


class Participant(ABC):
    def __init__(self, mediator: Mediator):
        self._mediator = mediator

    def send(self, message):
        self._mediator.relay(message, self)

    @abstractmethod
    def receive(self, message):
        pass
