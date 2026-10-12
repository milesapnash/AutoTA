import unittest

from src.languages.python.graph import build_python_graph
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
    return {(entity.type, entity.name) for entity in entities}


def related(graph, relation_type):
    return {(relation.source.name,
             relation.target.name)
            for relation in graph['relations']
            if relation.relation_type == relation_type}


def qualified(entity):
    """Names a member along with the class that it belongs to."""
    owners = entity.relations['memberOf']
    if owners and entity.type not in ('class', 'abstractClass', 'interface'):
        return f'{owners[0].name}.{entity.name}'
    return entity.name


def related_members(graph, relation_type):
    return {(qualified(relation.source), qualified(relation.target))
            for relation in graph['relations']
            if relation.relation_type == relation_type}


class TestPythonGraph(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = build(shapes=SHAPES, canvas=CANVAS)

    def test_entities(self):
        self.assertEqual(described(self.graph['entities']), {
            ('class', 'Colour'), ('field', 'RED'),
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
        modifiers = {entity.name: entity.modifiers
                     for entity in self.graph['entities']
                     if entity.type == 'field'}

        self.assertEqual(modifiers['_length'], {'private'})
        self.assertEqual(modifiers['sides'], {'public', 'static'})

    def test_extends_and_implements(self):
        self.assertEqual(related(self.graph, 'extends'), {('Square', 'Base')})
        self.assertEqual(related(self.graph, 'implements'),
                         {('Square', 'Shape')})

    def test_overrides(self):
        overrides = {(relation.source.type, relation.target.type,
                      relation.target.name)
                     for relation in self.graph['relations']
                     if relation.relation_type == 'overrides'}

        self.assertEqual(overrides, {('method', 'abstractMethod', 'area'),
                                     ('method', 'abstractMethod', 'name')})

    def test_invokes_and_instantiates(self):
        self.assertIn(('describe', 'name'), related(self.graph, 'invokes'))
        # A field instantiates the class that it is set to a new one of
        self.assertEqual(related(self.graph, 'instantiates'),
                         {('scaled', 'Square'),
                          ('Canvas Constructor', 'Square'),
                          ('_default', 'Square')})

    def test_parameter_and_return_types(self):
        self.assertEqual(related(self.graph, 'parameterOfType'),
                         {('Canvas Constructor', 'Shape'),
                          ('draw', 'Shape')})
        self.assertEqual(related(self.graph, 'hasReturnType'),
                         {('scaled', 'Square')})

    def test_field_types(self):
        # From an annotation, from the parameter a field is set from, and
        # from the class instantiated; an untyped parameter gives no type.
        # The members of an enum are of its own type
        self.assertEqual(related(self.graph, 'isOfType'),
                         {('background', 'Shape'), ('_shape', 'Shape'),
                          ('_default', 'Square'), ('RED', 'Colour')})


OBSERVERS = '''
from abc import ABC, abstractmethod
from typing import Optional


class Observer(ABC):
    @abstractmethod
    def update(self, key):
        pass


class Subject:
    class Memo:
        def value(self):
            return 1

    _instance = None

    def __init__(self, first: Observer, untyped):
        self._observers: list[Observer] = [first]
        self._by_topic: dict[str, list[Observer]] = {}
        self._main: Optional[Observer] = None
        self._other: Observer | None = None
        self._untyped = untyped
        self._memo = Subject.Memo()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls(None, None)
        return cls._instance

    def notify(self, key):
        for observer in self._observers:
            observer.update(key)

    def notify_first(self, key):
        self._observers[0].update(key)

    def notify_main(self, key):
        self._main.update(key)

    def memo(self):
        return self._memo.value()

    def observers(self) -> list[Observer]:
        return self._observers
'''


class TestTypedRelations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = build(observers=OBSERVERS)

    def test_field_is_a_collection_of_the_types_it_is_annotated_with(self):
        self.assertEqual(related(self.graph, 'isCollectionOf'),
                         {('_observers', 'Observer'),
                          ('_by_topic', 'Observer')})

    def test_optional_annotations_hold_a_single_value(self):
        self.assertEqual(related(self.graph, 'isOfType'),
                         {('_main', 'Observer'), ('_other', 'Observer'),
                          ('_memo', 'Memo')})

    def test_return_type_includes_what_it_is_a_collection_of(self):
        self.assertEqual(related(self.graph, 'hasReturnType'),
                         {('observers', 'Observer')})

    def test_nested_class_belongs_to_outer_class(self):
        self.assertIn(('Subject', 'Memo'), related(self.graph, 'has'))

    def test_method_is_found_from_the_type_it_is_called_on(self):
        self.assertEqual(related_members(self.graph, 'invokes'),
                         {('Subject.notify', 'Observer.update'),
                          ('Subject.notify_first', 'Observer.update'),
                          ('Subject.notify_main', 'Observer.update'),
                          ('Subject.memo', 'Memo.value')})

    def test_instantiates_through_cls_and_nested_class(self):
        # A field instantiates the class that it is set to a new one of
        self.assertEqual(related(self.graph, 'instantiates'),
                         {('instance', 'Subject'), ('_instance', 'Subject'),
                          ('Subject Constructor', 'Memo'),
                          ('_memo', 'Memo')})

    def test_member_assigns_the_fields_it_sets(self):
        self.assertLessEqual({('instance', '_instance'),
                              ('Subject Constructor', '_observers'),
                              ('Subject Constructor', '_untyped')},
                             related(self.graph, 'assigns'))

    def test_method_returns_the_field_it_gives_back(self):
        self.assertEqual(related(self.graph, 'returns'),
                         {('instance', '_instance'),
                          ('observers', '_observers')})


class TestResolution(unittest.TestCase):
    def test_method_overrides_through_the_whole_hierarchy(self):
        graph = build(shapes='''
from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def area(self):
        pass


class Base(Shape, ABC):
    def describe(self):
        return 'shape'


class Square(Base):
    def area(self):
        return 1

    def describe(self):
        return 'square'
''')

        self.assertEqual(related_members(graph, 'overrides'),
                         {('Square.area', 'Shape.area'),
                          ('Square.describe', 'Base.describe')})

    def test_unknown_receiver_falls_back_to_the_only_method_of_that_name(
            self):
        graph = build(report='''
import os


class Printer:
    def print_all(self):
        pass

    def join(self):
        pass

    def flush(self):
        pass


class Spooler:
    def flush(self):
        pass


class Report:
    def run(self, untyped):
        untyped.print_all()
        untyped.flush()
        os.path.join('a', 'b')
''')

        # A module is known not to be one of the project's classes
        self.assertEqual(related_members(graph, 'invokes'),
                         {('Report.run', 'Printer.print_all')})

    def test_enum_members_are_fields_of_its_own_type(self):
        graph = build(colours='''
from enum import Enum


class Colour(Enum):
    RED = 1
    GREEN = 2

    def label(self):
        return self.name
''')

        self.assertEqual(described(graph['entities']),
                         {('class', 'Colour'), ('field', 'RED'),
                          ('field', 'GREEN'), ('method', 'label')})
        self.assertEqual(related(graph, 'isOfType'),
                         {('RED', 'Colour'), ('GREEN', 'Colour')})

    def test_shared_name_is_found_by_import(self):
        graph = build(
            first='class Token:\n    pass\n',
            second='class Token:\n    pass\n',
            importer='from second import Token\n\n\n'
                     'class Importer:\n    token: Token\n',
            stranger='class Stranger:\n    token: Token\n')

        files = {relation.source.file: relation.target.file
                 for relation in graph['relations']
                 if relation.relation_type == 'isOfType'}

        # Neither Token is visible from a file that does not import one
        self.assertEqual(files, {'importer.py': 'second.py'})


if __name__ == '__main__':
    unittest.main()
