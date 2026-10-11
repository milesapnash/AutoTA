from connection_state import ConnectionState


class ClosedState(ConnectionState):
    def send(self, connection, data):
        print("Connection closed")
