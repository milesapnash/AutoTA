from key_collection import KeyCollection
from key_ring_iterator import KeyRingIterator


class KeyRing(KeyCollection):
    def __init__(self, keys: list[str]):
        self._keys = keys

    def create_iterator(self):
        return KeyRingIterator(self._keys)
