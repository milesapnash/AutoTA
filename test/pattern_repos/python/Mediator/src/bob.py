from participant import Participant


class Bob(Participant):
    def receive(self, message):
        print(f"Bob received {message}")
