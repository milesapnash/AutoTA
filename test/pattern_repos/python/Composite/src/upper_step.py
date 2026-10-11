from crypto_step import CryptoStep


class UpperStep(CryptoStep):
    def apply(self, text):
        return text.upper()
