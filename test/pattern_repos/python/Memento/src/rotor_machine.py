from rotor_memento import RotorMemento


class RotorMachine:
    def __init__(self):
        self._position = 0

    def advance(self):
        self._position = (self._position + 1) % 26

    def save(self) -> RotorMemento:
        return RotorMemento(self._position)

    def restore(self, memento: RotorMemento):
        self._position = memento.get_position()
