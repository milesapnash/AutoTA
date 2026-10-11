from context import Context
from expression import Expression


class SequenceExpression(Expression):
    def __init__(self, first: Expression, second: Expression):
        self._first = first
        self._second = second

    def interpret(self, context: Context):
        self._first.interpret(context)
        self._second.interpret(context)
