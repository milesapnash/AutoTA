from cipher_engine import CipherEngine
from command import Command


class DecryptCommand(Command):
    def __init__(self, engine: CipherEngine, text):
        self._engine = engine
        self._text = text

    def execute(self):
        self._engine.decrypt(self._text)
