from key_iterator import KeyIterator


class KeyRingIterator(KeyIterator):
    def __init__(self, keys: list[str]):
        self._keys = keys
        self._position = 0

    def has_next(self):
        return self._position < len(self._keys)

    def next(self):
        key = self._keys[self._position]
        self._position += 1
        return key
