class Signer:
    def sign(self, text, key):
        return f"sig({text},{key})"
