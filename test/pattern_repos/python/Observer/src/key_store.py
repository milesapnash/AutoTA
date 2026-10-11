from key_observer import KeyObserver


class KeyStore:
    def __init__(self):
        self._observers: list[KeyObserver] = []
        self._key = None

    def attach(self, observer: KeyObserver):
        self._observers.append(observer)

    def detach(self, observer: KeyObserver):
        self._observers.remove(observer)

    def set_key(self, key):
        self._key = key
        self._notify_observers()

    def _notify_observers(self):
        for observer in self._observers:
            observer.update(self._key)
