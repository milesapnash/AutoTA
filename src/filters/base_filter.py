class Filter:
    def __init__(self, language):
        self.language = language

    def get_nodes(self, ast):
        return ast

    @staticmethod
    def name_of(node):
        raise NotImplementedError

    @staticmethod
    def line_of(node):
        raise NotImplementedError
