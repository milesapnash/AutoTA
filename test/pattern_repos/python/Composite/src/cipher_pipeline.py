from crypto_step import CryptoStep


class CipherPipeline(CryptoStep):
    def __init__(self):
        self._steps: list[CryptoStep] = []

    def add(self, step: CryptoStep):
        self._steps.append(step)

    def apply(self, text):
        for step in self._steps:
            text = step.apply(text)
        return text
