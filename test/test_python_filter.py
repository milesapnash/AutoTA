import ast
import unittest

from src.filters.python_filter import PythonFilter

CODE = '''
from abc import ABC, abstractmethod
from enum import Enum
from typing import Protocol


class Colour(Enum):
    RED = 1


class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass


class Drawable(Protocol):
    def draw(self): ...


class Base(ABC):
    def describe(self):
        return self.name()

    @abstractmethod
    def name(self):
        pass


class Square(Shape):
    sides: int = 4
    _instances = 0

    def __init__(self, length):
        self.length = length
        self._cache = None
        local = length * 2
        self.length = local

    def area(self) -> float:
        self._cache = self.length ** 2
        return self._cache

    @staticmethod
    def unit():
        return Square(1)

    def _reset(self):
        self._cache = None


def helper():
    value = 1
    return value
'''


def names(nodes):
    return [PythonFilter.name_of(node) for node in nodes]


class TestPythonFilter(unittest.TestCase):
    def setUp(self):
        self.tree = ast.parse(CODE)

    def find(self, **options):
        return names(PythonFilter(**options).get_nodes(self.tree))

    def test_classes_exclude_interfaces_and_enums(self):
        self.assertEqual(self.find(node_class='class'), ['Base', 'Square'])
        self.assertEqual(self.find(node_class='interface'),
                         ['Shape', 'Drawable'])
        self.assertEqual(self.find(node_class='enum'), ['Colour'])

    def test_constructor_is_not_a_method(self):
        self.assertEqual(self.find(node_class='constructor'), ['__init__'])
        self.assertNotIn('__init__', self.find(node_class='method'))
        self.assertIn('helper', self.find(node_class='method'))

    def test_fields_exclude_local_variables_and_repeats(self):
        square = PythonFilter(node_class='class',
                              node_name='Square').get_nodes(self.tree)[0]
        fields = names(PythonFilter(node_class='field').get_nodes(square))

        self.assertEqual(fields,
                         ['sides', '_instances', 'length', '_cache'])

    def test_leading_underscore_is_private(self):
        self.assertEqual(
            self.find(node_class='field', node_modifiers=['private']),
            ['_instances', '_cache'])
        self.assertEqual(
            self.find(node_class='method', node_modifiers=['private']),
            ['_reset'])

    def test_negated_modifiers(self):
        square = PythonFilter(node_class='class',
                              node_name='Square').get_nodes(self.tree)[0]
        public = names(PythonFilter(node_class='field',
                                    node_modifiers=['private'],
                                    negatives=['node_modifiers'])
                       .get_nodes(square))

        self.assertEqual(public, ['sides', 'length'])

    def test_static_and_abstract_modifiers(self):
        self.assertEqual(
            self.find(node_class='method', node_modifiers=['static']),
            ['unit'])
        self.assertEqual(
            self.find(node_class='method', node_modifiers=['abstract']),
            ['area', 'name'])
        self.assertEqual(
            self.find(node_class='field', node_modifiers=['static']),
            ['RED', 'sides', '_instances'])

    def test_decorators_are_annotations(self):
        self.assertEqual(
            self.find(node_class='method',
                      node_annotations=['abstractmethod']),
            ['area', 'name'])

    def test_extends_and_types(self):
        self.assertEqual(self.find(node_class='class', node_extends='Shape'),
                         ['Square'])
        self.assertEqual(self.find(node_class='field', node_type='int'),
                         ['sides'])
        self.assertEqual(
            self.find(node_class='method', node_return_type='float'),
            ['area', 'area'])

    def test_unknown_node_class_is_rejected(self):
        with self.assertRaises(ValueError):
            PythonFilter(node_class='klass')


if __name__ == '__main__':
    unittest.main()
