from key_observer import KeyObserver


class CacheInvalidator(KeyObserver):
    def update(self, key):
        print(f"Cache cleared for {key}")
