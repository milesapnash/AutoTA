import unittest

from src.entity_relations.python_graph import build_python_graph
from src.project.review_file import ReviewFile

SHAPES = '''
from abc import ABC, abstractmethod
from enum import Enum


class Colour(Enum):
    RED = 1


class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass


class Base(ABC):
    def describe(self):
        return self.name()

    @abstractmethod
    def name(self):
        pass


class Square(Base, Shape):
    sides: int = 4

    def __init__(self, length):
        self._length = length

    def area(self) -> float:
        return self._length ** 2

    def name(self):
        return 'square'

    def scaled(self, factor) -> 'Square':
        return Square(self._length * factor)


def helper():
    return Square(1)
'''

CANVAS = '''
from shapes import Shape, Square


class Canvas:
    background: Shape

    def __init__(self, shape: Shape, size):
        self._shape = shape
        self._default = Square(1)
        self._size = size

    def draw(self, shape: Shape):
        return shape.area()
'''


def build(**sources):
    files = [ReviewFile('./', '', f'{name}.py', contents=code)
             for name, code in sources.items()]
    return build_python_graph(files)


def described(entities):
    return {(entity.type, entity.info['name']) for entity in entities}


def related(graph, relation_type):
    return {(relation.entity_from.info['name'],
             relation.entity_to.info['name'])
            for relation in graph['relations']
            if relation.relation_type == relation_type}


class TestPythonGraph(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = build(shapes=SHAPES, canvas=CANVAS)

    def test_entities(self):
        self.assertEqual(described(self.graph['entities']), {
            ('interface', 'Shape'), ('abstractMethod', 'area'),
            ('abstractClass', 'Base'), ('method', 'describe'),
            ('abstractMethod', 'name'),
            ('class', 'Square'), ('field', 'sides'),
            ('constructor', 'Square Constructor'), ('field', '_length'),
            ('method', 'area'), ('method', 'name'), ('method', 'scaled'),
            ('class', 'Canvas'), ('field', 'background'),
            ('constructor', 'Canvas Constructor'), ('field', '_shape'),
            ('field', '_default'), ('field', '_size'), ('method', 'draw')})

    def test_members_belong_to_their_class(self):
        self.assertEqual(
            {member for owner, member in related(self.graph, 'has')
             if owner == 'Canvas'},
            {'background', 'Canvas Constructor', '_shape', '_default',
             '_size', 'draw'})

    def test_modifiers(self):
        modifiers = {entity.info['name']: entity.info['modifiers']
                     for entity in self.graph['entities']
                     if entity.type == 'field'}

        self.assertEqual(modifiers['_length'], {'private'})
        self.assertEqual(modifiers['sides'], {'public', 'static'})

    def test_extends_and_implements(self):
        self.assertEqual(related(self.graph, 'extends'), {('Square', 'Base')})
        self.assertEqual(related(self.graph, 'implements'),
                         {('Square', 'Shape')})

    def test_overrides(self):
        overrides = {(relation.entity_from.type, relation.entity_to.type,
                      relation.entity_to.info['name'])
                     for relation in self.graph['relations']
                     if relation.relation_type == 'overrides'}

        self.assertEqual(overrides, {('method', 'abstractMethod', 'area'),
                                     ('method', 'abstractMethod', 'name')})

    def test_invokes_and_instantiates(self):
        self.assertIn(('describe', 'name'), related(self.graph, 'invokes'))
        self.assertEqual(related(self.graph, 'instantiates'),
                         {('scaled', 'Square'),
                          ('Canvas Constructor', 'Square')})

    def test_parameter_and_return_types(self):
        self.assertEqual(related(self.graph, 'parameterOfType'),
                         {('Canvas Constructor', 'Shape'),
                          ('draw', 'Shape')})
        self.assertEqual(related(self.graph, 'hasReturnType'),
                         {('scaled', 'Square')})

    def test_field_types(self):
        # From an annotation, from the parameter a field is set from, and
        # from the class instantiated; an untyped parameter gives no type
        self.assertEqual(related(self.graph, 'isOfType'),
                         {('background', 'Shape'), ('_shape', 'Shape'),
                          ('_default', 'Square')})


if __name__ == '__main__':
    unittest.main()
