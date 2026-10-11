from connection_state import ConnectionState
from encrypted_state import EncryptedState


class HandshakeState(ConnectionState):
    def send(self, connection, data):
        print("Handshake complete")
        connection.set_state(EncryptedState())
