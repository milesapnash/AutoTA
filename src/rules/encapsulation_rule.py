from src.filters.java_filter import JavaFilter
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
        if file.language == 'java':
            for ast_class in JavaFilter(node_class='class').get_nodes(ast):
                visible_fields = JavaFilter(node_class='field',
                                            node_modifiers=['private'],
                                            negatives=[
                                                'node_modifiers']).get_nodes(
                    ast_class)

                for field in visible_fields:
                    line, char = field.position
                    name = field.declarators[0].name
                    feedback.append(
                        (line, f'In class {ast_class.name}, the {name} '
                               f'field is not private'))

                if self._getters:
                    pass

                if self._setters:
                    pass

        return feedback

    def __str__(self):
        return '-Encapsulation Rule'
