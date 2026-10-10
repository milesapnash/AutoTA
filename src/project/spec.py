from src.entity_relations.design_pattern import DesignPattern
from src.filters.java_filter import JavaFilter
from src.rules.encapsulation_rule import EncapsulationRule
from src.rules.identifier_rule import IdentifierRule


def build_spec(spec_file):
    task = 'Cryptography Task'
    rules = [EncapsulationRule(scope=('dir', 'main')), IdentifierRule(
        node_filter=JavaFilter(node_class='method',
                               node_annotations=[
                                   'Test'],
                               node_name=r"^test"))]
    patterns = [DesignPattern('templateMethod')]

    return Spec(task, rules=rules, patterns=patterns)


class Spec:
    def __init__(self, task, rules=None, patterns=None):
        self.task = task
        self.rules = rules
        self.patterns = patterns
