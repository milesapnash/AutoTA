from abc import ABC, abstractmethod

from key_iterator import KeyIterator


class KeyCollection(ABC):
    @abstractmethod
    def create_iterator(self) -> KeyIterator:
        pass
