from src.languages import LANGUAGES
from src.rules.rule import Rule


# Checks that all classes within scope are Encapsulated
class EncapsulationRule(Rule):
    def __init__(self, scope='project', getters=False, setters=False):
        super().__init__(scope)
        self._getters = getters
        self._setters = setters

    def apply(self, file):
        ast = self.file_filter(file)
        if ast is None:
            return []

        feedback = []
        node_filter = LANGUAGES[file.language].filter
        for ast_class in node_filter(node_class='class').get_nodes(ast):
            visible_fields = node_filter(node_class='field',
                                         node_modifiers=['private'],
                                         negatives=['node_modifiers']
                                         ).get_nodes(ast_class)

            for field in visible_fields:
                feedback.append(
                    (node_filter.line_of(field),
                     f'In class {node_filter.name_of(ast_class)}, the '
                     f'{node_filter.name_of(field)} field is not private'))

            if self._getters:
                pass

            if self._setters:
                pass

        return feedback

    def __str__(self):
        return '-Encapsulation Rule'
