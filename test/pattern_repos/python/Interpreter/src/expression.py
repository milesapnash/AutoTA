from abc import ABC, abstractmethod

from context import Context


class Expression(ABC):
    @abstractmethod
    def interpret(self, context: Context):
        pass
