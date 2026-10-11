from key_observer import KeyObserver


class AuditLogger(KeyObserver):
    def update(self, key):
        print(f"Key rotated: {key}")
