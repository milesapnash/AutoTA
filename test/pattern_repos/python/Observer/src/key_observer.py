from abc import ABC, abstractmethod


class KeyObserver(ABC):
    @abstractmethod
    def update(self, key):
        pass
