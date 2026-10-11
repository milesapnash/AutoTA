from cipher_engine import CipherEngine
from command import Command


class EncryptCommand(Command):
    def __init__(self, engine: CipherEngine, text):
        self._engine = engine
        self._text = text

    def execute(self):
        self._engine.encrypt(self._text)
