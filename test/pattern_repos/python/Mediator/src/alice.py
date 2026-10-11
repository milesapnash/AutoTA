from participant import Participant


class Alice(Participant):
    def receive(self, message):
        print(f"Alice received {message}")
