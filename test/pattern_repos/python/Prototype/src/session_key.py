from key import Key


class SessionKey(Key):
    def __init__(self, material):
        self._material = material

    def copy(self) -> Key:
        return SessionKey(self._material)
