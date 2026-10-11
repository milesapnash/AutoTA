from crypto_step import CryptoStep


class ReverseStep(CryptoStep):
    def apply(self, text):
        return text[::-1]
