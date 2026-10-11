from mediator import Mediator
from participant import Participant


class KeyExchangeServer(Mediator):
    def __init__(self):
        self._participants: list[Participant] = []

    def register(self, participant: Participant):
        self._participants.append(participant)

    def relay(self, message, sender: Participant):
        for participant in self._participants:
            if participant is not sender:
                participant.receive(message)
