import os
import unittest

from src.entity_relations.design_pattern import DesignPattern
from src.entity_relations.java_graph import build_java_graph
from src.project.review_file import ReviewFile
from src.project.review_project import ReviewProject
from src.project.spec import Spec

PATTERN_REPOS = os.path.join(os.path.dirname(__file__), 'pattern_repos',
                             'java')


def detect(repo, pattern):
    """Runs pattern detection on a fixture repo and returns the feedback."""
    spec = Spec('pattern test', 'java', patterns=[DesignPattern(pattern)])
    project = ReviewProject(os.path.join(PATTERN_REPOS, repo), spec)
    return '\n'.join(project.feedback)


class TestPatternsFound(unittest.TestCase):
    def assert_found(self, feedback, pattern, expected_entities):
        self.assertIn(f'Found potential instance of {pattern} pattern',
                      feedback)
        for entity in expected_entities:
            self.assertIn(entity, feedback)

    def test_singleton_found(self):
        feedback = detect('Singleton', 'singleton')

        self.assert_found(feedback, 'singleton',
                          ['class: Singleton',
                           'constructor: Singleton Constructor',
                           'field: instance', 'method: getInstance'])

    def test_template_method_found(self):
        feedback = detect('TemplateMethod', 'templateMethod')

        self.assert_found(feedback, 'templateMethod',
                          ['abstractClass: TemplateT',
                           'abstractMethod: doSomethingFirst',
                           'method: doSomething',
                           'class: ExtenderA', 'class: ExtenderB'])

    def test_strategy_found(self):
        feedback = detect('Strategy', 'strategy')

        self.assert_found(feedback, 'strategy',
                          ['class: ContextC', 'interface: Strategy',
                           'abstractMethod: algorithm',
                           'class: ConcreteStrategyA',
                           'class: ConcreteStrategyB'])


class TestPatternsNotFound(unittest.TestCase):
    def test_patterns_not_found_in_other_pattern_repos(self):
        cases = [('Strategy', 'templateMethod'),
                 ('Strategy', 'singleton'),
                 ('TemplateMethod', 'strategy'),
                 ('TemplateMethod', 'singleton'),
                 ('Singleton', 'strategy'),
                 ('Singleton', 'templateMethod')]
        for repo, pattern in cases:
            with self.subTest(repo=repo, pattern=pattern):
                feedback = detect(repo, pattern)

                self.assertIn(
                    f'Could not find any potential instances of {pattern} '
                    f'pattern', feedback)

    def test_singleton_with_public_constructor_is_almost_complete(self):
        feedback = detect('SingletonPublicConstructor', 'singleton')

        self.assertIn('almost complete', feedback)
        self.assertIn('MISSING ENTITY: private constructor', feedback)

    def test_template_method_without_subclass_is_almost_complete(self):
        feedback = detect('TemplateMethodIncomplete', 'templateMethod')

        self.assertIn('almost complete', feedback)
        self.assertIn('MISSING ENTITY: subclass', feedback)

    def test_strategy_without_concrete_strategies_is_not_found(self):
        feedback = detect('StrategyIncomplete', 'strategy')

        self.assertIn('Could not find any potential instances of strategy '
                      'pattern', feedback)


class TestErGraph(unittest.TestCase):
    def test_file_without_package_declaration_builds_graph(self):
        code = """
        public class Example {
            private int field;
            public void method() {}
        }
        """
        file = ReviewFile('./', '', 'Example.java', contents=code)

        graph = build_java_graph([file])

        names = {entity.info['name'] for entity in graph['entities']}
        self.assertEqual(names, {'Example', 'field', 'method'})


if __name__ == '__main__':
    unittest.main()
