from connection_state import ConnectionState


class EncryptedState(ConnectionState):
    def send(self, connection, data):
        print(f"Sending encrypted {data}")
