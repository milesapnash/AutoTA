from src.languages.java.filter import JavaFilter
from src.languages.python.filter import PythonFilter
from src.patterns.design_pattern import DesignPattern
from src.rules.encapsulation_rule import EncapsulationRule
from src.rules.identifier_rule import IdentifierRule


def build_spec():
    task = 'Cryptography Task'
    rules = [EncapsulationRule(scope='main'),
             # Java test names should not start with 'test'
             IdentifierRule(
                 node_filter=JavaFilter(node_class='method',
                                        node_annotations=['Test'],
                                        node_name=r"^test")),
             # Python method names should be in snake case
             IdentifierRule(
                 node_filter=PythonFilter(node_class='method',
                                          node_name=r".*[a-z][A-Z]"))]
    patterns = [DesignPattern('templateMethod')]

    return Spec(task, rules=rules, patterns=patterns)


class Spec:
    def __init__(self, task, rules=None, patterns=None):
        self.task = task
        self.rules = rules
        self.patterns = patterns
