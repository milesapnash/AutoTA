from strategy import Strategy


class ContextC:
    def __init__(self, strategy: Strategy):
        self._strategy = strategy

    def operation(self):
        self._strategy.algorithm()
