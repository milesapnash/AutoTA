from rotor_memento import RotorMemento


class RotorHistory:
    def __init__(self):
        self._history: list[RotorMemento] = []

    def push(self, memento: RotorMemento):
        self._history.append(memento)

    def pop(self) -> RotorMemento:
        return self._history.pop()
