import unittest

from src.filters.java_filter import JavaFilter
from src.filters.python_filter import PythonFilter
from src.project.review_file import ReviewFile
from src.rules.encapsulation_rule import EncapsulationRule
from src.rules.identifier_rule import IdentifierRule


class TestRules(unittest.TestCase):
    def test_positive_java_encapsulation_rule(self):
        code = """
        public class Example {
            private final String encapsulated = "test";
            public String getEncapsulated() {
                return encapsulated;
            }
        }
        """
        file = ReviewFile('./', "", 'example.java', contents=code)
        results = EncapsulationRule().apply(file)

        self.assertEqual(results, [])

    def test_negative_java_encapsulation_rule(self):
        code = """
        public class Example {
            public String encapsulated;
            public String getEncapsulated() {
                return encapsulated;
            }
        }
        """
        file = ReviewFile('./', "", 'example.java', contents=code)
        results = EncapsulationRule().apply(file)

        self.assertEqual(len(results), 1)

    def test_positive_java_identifier_rule(self):
        code = """
        public class ExampleTest {
            @Test
            public void doesThing() {
                assertThat(1, is(1));
            }
        }
        """
        file = ReviewFile('./', "", 'example.java', contents=code)
        results = IdentifierRule(node_filter=JavaFilter(node_class='method',
                                                        node_name=r"^test")).apply(
            file)

        self.assertEqual(results, [])

    def test_negative_java_identifier_rule(self):
        code = """
        public class ExampleTest {
            @Test
            public void testThatDoesThing() {
                assertThat(1, is(1));
            }
        }
        """
        file = ReviewFile('./', "", 'example.java', contents=code)
        results = IdentifierRule(node_filter=JavaFilter(node_class='method',
                                                        node_name=r"^test")).apply(
            file)

        self.assertEqual(len(results), 1)

    def test_java_rules_apply_to_file_with_newer_syntax(self):
        code = """
        public class Example {
            public String visible;

            public String describe(Object value) {
                return switch (value) {
                    case String text -> text;
                    default -> "other";
                };
            }
        }

        record Point(int x, int y) {}
        """
        file = ReviewFile('./', "", 'example.java', contents=code)
        results = EncapsulationRule().apply(file)

        self.assertEqual(results, [
            (3, 'In class Example, the visible field is not private')])

    def test_java_filter_matches_every_node_by_default(self):
        code = 'class Example { int count; void run() {} }'
        file = ReviewFile('./', "", 'example.java', contents=code)

        nodes = JavaFilter().get_nodes(file.ast)

        self.assertLessEqual({'class_declaration', 'field_declaration',
                              'method_declaration'},
                             {node.type for node in nodes})

    def test_java_filter_rejects_an_unknown_node_class(self):
        with self.assertRaises(ValueError):
            JavaFilter(node_class='package')

    def test_java_filter_matches_annotations_and_supertypes(self):
        code = """
        @Deprecated
        public class Example extends Base implements Runnable, Shape {
            @Override
            public void run() {}

            public int area() { return 1; }
        }
        """
        file = ReviewFile('./', "", 'example.java', contents=code)

        def names(**criteria):
            return [JavaFilter.name_of(node) for node in
                    JavaFilter(**criteria).get_nodes(file.ast)]

        self.assertEqual(names(node_class='method',
                               node_annotations=['Override']), ['run'])
        self.assertEqual(names(node_class='method',
                               node_return_type='int'), ['area'])
        self.assertEqual(names(node_class='class', node_extends='Base',
                               node_implements=['Shape']), ['Example'])
        self.assertEqual(names(node_class='class', node_extends='Other'),
                         [])

    def test_positive_python_encapsulation_rule(self):
        code = """
class Example:
    _count = 0

    def __init__(self):
        self._encapsulated = "test"

    def get_encapsulated(self):
        return self._encapsulated
"""
        file = ReviewFile('./', "", 'example.py', contents=code)
        results = EncapsulationRule().apply(file)

        self.assertEqual(results, [])

    def test_negative_python_encapsulation_rule(self):
        code = """
class Example:
    count = 0

    def __init__(self):
        self.encapsulated = "test"

    def get_encapsulated(self):
        return self.encapsulated
"""
        file = ReviewFile('./', "", 'example.py', contents=code)
        results = EncapsulationRule().apply(file)

        self.assertEqual(results, [
            (3, 'In class Example, the count field is not private'),
            (6, 'In class Example, the encapsulated field is not private')])

    def test_positive_python_identifier_rule(self):
        code = """
class Example:
    def get_encapsulated(self):
        return self._encapsulated
"""
        file = ReviewFile('./', "", 'example.py', contents=code)
        results = IdentifierRule(
            node_filter=PythonFilter(node_class='method',
                                     node_name=r'.*[A-Z].*')).apply(file)

        self.assertEqual(results, [])

    def test_negative_python_identifier_rule(self):
        code = """
class Example:
    def getEncapsulated(self):
        return self._encapsulated
"""
        file = ReviewFile('./', "", 'example.py', contents=code)
        results = IdentifierRule(
            node_filter=PythonFilter(node_class='method',
                                     node_name=r'.*[A-Z].*')).apply(file)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 3)


if __name__ == '__main__':
    unittest.main()
