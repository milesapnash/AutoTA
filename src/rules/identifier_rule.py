from src.rules.rule import Rule


# Checks that all nodes within scope follow naming convention
class IdentifierRule(Rule):
    def __init__(self, scope='project', node_filter=None):
        super().__init__(scope)
        self.node_filter = node_filter

    def applies_to(self, language):
        # A filter only applies to the language it was written for
        return self.node_filter is None or (
                self.node_filter.language == language)

    def apply(self, file):
        ast = self.file_filter(file)
        if ast is None or self.node_filter is None:
            return []
        if not self.applies_to(file.language):
            return []

        feedback = []
        for node in self.node_filter.get_nodes(ast):
            feedback.append(
                (self.node_filter.line_of(node),
                 f'The {self.node_filter.node_class}, '
                 f'{self.node_filter.name_of(node)}, does not follow the '
                 f'specified naming convention.'))

        return feedback

    def passed_message(self):
        return (f'All {self.node_filter.node_class}s within {self.scope} '
                f'had the correct identifier format of '
                f'{self.node_filter.node_name}')

    def __str__(self):
        return '-Identifier Rule'
