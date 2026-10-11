from closed_state import ClosedState
from connection_state import ConnectionState
from handshake_state import HandshakeState


class SecureConnection:
    def __init__(self):
        self._state: ConnectionState = HandshakeState()

    def set_state(self, state: ConnectionState):
        self._state = state

    def send(self, data):
        self._state.send(self, data)

    def close(self):
        self._state = ClosedState()
