from key import Key


class KeyRegistry:
    def __init__(self):
        self._prototypes: dict[str, Key] = {}

    def register(self, name, prototype: Key):
        self._prototypes[name] = prototype

    def create(self, name):
        return self._prototypes[name].copy()
