import os
import unittest

from src.entity_relations.design_pattern import DesignPattern
from src.entity_relations.java_graph import build_java_graph
from src.project.review_file import ReviewFile
from src.project.review_project import ReviewProject
from src.project.spec import Spec

PATTERN_REPOS = os.path.join(os.path.dirname(__file__), 'pattern_repos')


def detect(repo, pattern, language='java'):
    """Runs pattern detection on a fixture repo and returns the feedback."""
    spec = Spec('pattern test', patterns=[DesignPattern(pattern)])
    project = ReviewProject(os.path.join(PATTERN_REPOS, language, repo),
                            spec)
    return '\n'.join(project.feedback)


class PatternTestCase(unittest.TestCase):
    def assert_found(self, feedback, pattern, expected_entities):
        self.assertIn(f'Found potential instance of {pattern} pattern',
                      feedback)
        for entity in expected_entities:
            self.assertIn(entity, feedback)

    def assert_not_found(self, feedback, pattern):
        self.assertIn(
            f'Could not find any potential instances of {pattern} pattern',
            feedback)

    def assert_almost_complete(self, feedback, missing_entity):
        self.assertIn('almost complete', feedback)
        self.assertIn(f'MISSING ENTITY: {missing_entity}', feedback)


class TestPatternsFound(PatternTestCase):
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


class TestPatternsNotFound(PatternTestCase):
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


class TestPythonPatterns(PatternTestCase):
    def test_singleton_found(self):
        feedback = detect('Singleton', 'singleton', 'python')

        self.assert_found(feedback, 'singleton',
                          ['class: Singleton', 'field: _instance',
                           'method: get_instance'])

    def test_singleton_using_new_found(self):
        feedback = detect('SingletonNew', 'singleton', 'python')

        self.assert_found(feedback, 'singleton',
                          ['class: Singleton', 'field: _instance',
                           'method: __new__'])

    def test_template_method_found(self):
        feedback = detect('TemplateMethod', 'templateMethod', 'python')

        self.assert_found(feedback, 'templateMethod',
                          ['abstractClass: TemplateT',
                           'abstractMethod: do_something_first',
                           'method: do_something',
                           'class: ExtenderA', 'class: ExtenderB'])

    def test_strategy_found(self):
        feedback = detect('Strategy', 'strategy', 'python')

        self.assert_found(feedback, 'strategy',
                          ['class: ContextC', 'field: _strategy',
                           'interface: Strategy',
                           'abstractMethod: algorithm',
                           'class: ConcreteStrategyA',
                           'class: ConcreteStrategyB'])

    def test_patterns_not_found_in_other_pattern_repos(self):
        cases = [('Strategy', 'templateMethod'),
                 ('Strategy', 'singleton'),
                 ('TemplateMethod', 'strategy'),
                 ('TemplateMethod', 'singleton'),
                 ('Singleton', 'strategy'),
                 ('Singleton', 'templateMethod')]
        for repo, pattern in cases:
            with self.subTest(repo=repo, pattern=pattern):
                self.assert_not_found(detect(repo, pattern, 'python'),
                                      pattern)

    def test_singleton_with_public_instance_is_almost_complete(self):
        feedback = detect('SingletonPublicInstance', 'singleton', 'python')

        self.assert_almost_complete(feedback, 'private instance')

    def test_template_method_without_subclass_is_almost_complete(self):
        feedback = detect('TemplateMethodIncomplete', 'templateMethod',
                          'python')

        self.assert_almost_complete(feedback, 'subclass')

    def test_strategy_without_concrete_strategies_is_not_found(self):
        self.assert_not_found(
            detect('StrategyIncomplete', 'strategy', 'python'), 'strategy')


# The entities expected in the feedback for each of the remaining Gang of Four
# patterns. Class and interface names are the same in both languages.
GANG_OF_FOUR_PATTERNS = [
    ('AbstractFactory', 'abstractFactory',
     ['interface: CryptoFactory', 'interface: Cipher', 'interface: Hash',
      'class: ModernCryptoFactory', 'class: LegacyCryptoFactory',
      'class: AesCipher', 'class: Md5Hash']),
    ('FactoryMethod', 'factoryMethod',
     ['abstractClass: Messenger', 'interface: Cipher',
      'class: CaesarMessenger', 'class: ReverseMessenger',
      'class: CaesarCipher']),
    ('Builder', 'builder',
     ['class: ConfigDirector', 'interface: ConfigBuilder',
      'class: CipherConfig', 'class: FastConfigBuilder',
      'class: SecureConfigBuilder']),
    ('Prototype', 'prototype',
     ['interface: Key', 'class: SessionKey', 'class: MasterKey']),
    ('Adapter', 'adapter',
     ['interface: Cipher', 'class: ScramblerAdapter',
      'class: LegacyScrambler']),
    ('Bridge', 'bridge',
     ['abstractClass: SecureChannel', 'interface: Cipher',
      'class: TextChannel', 'class: FileChannel', 'class: CaesarCipher',
      'class: XorCipher']),
    ('Composite', 'composite',
     ['interface: CryptoStep', 'class: ReverseStep', 'class: UpperStep',
      'class: CipherPipeline']),
    ('Decorator', 'decorator',
     ['interface: Encryptor', 'class: PlainEncryptor',
      'abstractClass: EncryptorDecorator', 'class: Base64Decorator',
      'class: ReverseDecorator']),
    ('Facade', 'facade',
     ['class: CryptoFacade', 'class: KeyDeriver', 'class: Encryptor',
      'class: Signer']),
    ('Flyweight', 'flyweight',
     ['interface: CipherAlgorithm', 'class: NamedAlgorithm',
      'class: AlgorithmFactory']),
    ('Proxy', 'proxy',
     ['interface: SecretStore', 'class: VaultStore',
      'class: ProtectedStore']),
    ('ChainOfResponsibility', 'chainOfResponsibility',
     ['abstractClass: CertificateCheck', 'class: ExpiryCheck',
      'class: SignatureCheck']),
    ('Command', 'command',
     ['interface: Command', 'class: EncryptCommand',
      'class: DecryptCommand', 'class: CipherEngine',
      'class: CommandQueue']),
    ('Interpreter', 'interpreter',
     ['interface: Expression', 'class: Context',
      'class: ReverseExpression', 'class: UpperExpression',
      'class: SequenceExpression']),
    ('Iterator', 'iterator',
     ['interface: KeyIterator', 'interface: KeyCollection',
      'class: KeyRing', 'class: KeyRingIterator']),
    ('Mediator', 'mediator',
     ['interface: Mediator', 'abstractClass: Participant', 'class: Alice',
      'class: Bob', 'class: KeyExchangeServer']),
    ('Memento', 'memento',
     ['class: RotorMachine', 'class: RotorMemento', 'class: RotorHistory']),
    ('Observer', 'observer',
     ['class: KeyStore', 'interface: KeyObserver', 'class: AuditLogger',
      'class: CacheInvalidator']),
    ('State', 'state',
     ['class: SecureConnection', 'interface: ConnectionState',
      'class: HandshakeState', 'class: EncryptedState',
      'class: ClosedState']),
    ('Visitor', 'visitor',
     ['interface: CryptoItem', 'interface: ItemVisitor',
      'class: SecretKey', 'class: Certificate', 'class: ExpiryAuditor',
      'class: ExportVisitor'])
]


class TestGangOfFourPatterns(PatternTestCase):
    def test_pattern_found_in_both_languages(self):
        for language in ('java', 'python'):
            for repo, pattern, entities in GANG_OF_FOUR_PATTERNS:
                with self.subTest(language=language, pattern=pattern):
                    feedback = detect(repo, pattern, language)

                    self.assert_found(feedback, pattern, entities)

    def test_pattern_not_found_in_unrelated_repo(self):
        # A strategy interface without implementations matches none of these
        for language in ('java', 'python'):
            for _, pattern, _ in GANG_OF_FOUR_PATTERNS:
                with self.subTest(language=language, pattern=pattern):
                    feedback = detect('StrategyIncomplete', pattern,
                                      language)

                    self.assert_not_found(feedback, pattern)

    def test_pattern_not_found_in_repo_of_similar_pattern(self):
        # Each repo has much of the structure of the pattern, but lacks what
        # sets the pattern apart from the one that the repo implements
        cases = [('Adapter', 'facade'), ('Adapter', 'proxy'),
                 ('Proxy', 'facade'), ('Decorator', 'bridge'),
                 ('Mediator', 'bridge'), ('Composite', 'interpreter'),
                 ('Visitor', 'composite'), ('State', 'observer'),
                 ('Iterator', 'flyweight'), ('Strategy', 'state'),
                 ('FactoryMethod', 'abstractFactory')]
        for language in ('java', 'python'):
            for repo, pattern in cases:
                with self.subTest(language=language, repo=repo,
                                  pattern=pattern):
                    feedback = detect(repo, pattern, language)

                    self.assertNotIn(
                        f'Found potential instance of {pattern} pattern',
                        feedback)


def find(repo, pattern, language='java'):
    """Returns the instances found of a pattern in a fixture repo."""
    project = ReviewProject(os.path.join(PATTERN_REPOS, language, repo),
                            Spec('pattern test',
                                 patterns=[DesignPattern(pattern)]))
    return project.pattern_matches[pattern]


def names(match, role):
    return [entity.info['name'] for entity in match.roles[role]]


class TestMatches(unittest.TestCase):
    def test_match_gives_the_entities_for_each_role(self):
        for language in ('java', 'python'):
            with self.subTest(language=language):
                matches = find('Strategy', 'strategy', language)

                self.assertEqual(len(matches), 1)
                self.assertEqual(matches[0].missing, [])
                self.assertEqual(names(matches[0], 'context'), ['ContextC'])
                self.assertEqual(names(matches[0], 'strategy'), ['Strategy'])
                self.assertEqual(
                    sorted(names(matches[0], 'concrete_strategy')),
                    ['ConcreteStrategyA', 'ConcreteStrategyB'])

    def test_entity_fills_one_role_at_a_time(self):
        # The composite implements the component, as a leaf does, and the
        # originator handles mementos, as the caretaker does
        cases = [('Composite', 'composite', 'leaf',
                  ['ReverseStep', 'UpperStep']),
                 ('Interpreter', 'interpreter', 'terminal',
                  ['ReverseExpression', 'UpperExpression']),
                 ('Memento', 'memento', 'caretaker', ['RotorHistory'])]
        for language in ('java', 'python'):
            for repo, pattern, role, expected in cases:
                with self.subTest(language=language, pattern=pattern):
                    matches = find(repo, pattern, language)

                    self.assertEqual(len(matches), 1)
                    self.assertEqual(sorted(names(matches[0], role)),
                                     expected)

    def test_separate_instances_are_separate_matches(self):
        code = """
        interface Sorter { void sort(); }
        class QuickSorter implements Sorter { public void sort() {} }
        class ListView {
            private Sorter sorter;
            void show() { sorter.sort(); }
        }

        interface Encoder { void encode(); }
        class Base64Encoder implements Encoder { public void encode() {} }
        class Uploader {
            private Encoder encoder;
            void upload() { encoder.encode(); }
        }

        class Unrelated { void run() {} }
        """
        graph = build_java_graph([ReviewFile('./', '', 'Example.java',
                                             contents=code)])

        matches = DesignPattern('strategy').find_matches(graph, 'java')

        found = {(names(match, 'context')[0], names(match, 'strategy')[0],
                  names(match, 'concrete_strategy')[0])
                 for match in matches}
        self.assertEqual(found,
                         {('ListView', 'Sorter', 'QuickSorter'),
                          ('Uploader', 'Encoder', 'Base64Encoder')})
        for match in matches:
            self.assertEqual(names(match, 'concrete_method'),
                             ['sort' if names(match, 'strategy') == ['Sorter']
                              else 'encode'])

    def test_roles_need_different_entities(self):
        # A facade brings together two subsystems, not the same one twice
        code = """
        class Engine { void start() {} }
        class Car {
            private Engine engine;
            void drive() { engine.start(); engine.start(); }
        }
        """
        graph = build_java_graph([ReviewFile('./', '', 'Example.java',
                                             contents=code)])

        matches = DesignPattern('facade').find_matches(graph, 'java')

        self.assertEqual([match for match in matches if not match.missing],
                         [])

    def test_almost_complete_match_names_what_is_missing(self):
        matches = find('TemplateMethodIncomplete', 'templateMethod')

        self.assertEqual(len(matches), 1)
        # Nothing overrides the abstract methods without a subclass
        self.assertEqual(matches[0].missing, ['subclass', 'override'])
        self.assertEqual(names(matches[0], 'template'), ['TemplateT'])
        self.assertNotIn('subclass', matches[0].roles)

    def test_role_related_to_itself(self):
        # The handler's handle method invokes itself on the next handler
        matches = find('ChainOfResponsibility', 'chainOfResponsibility')

        self.assertEqual(names(matches[0], 'handle'), ['handle'])


class TestDesignPattern(unittest.TestCase):
    def test_unknown_pattern_is_rejected(self):
        with self.assertRaises(ValueError):
            DesignPattern('notAPattern')


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

    def test_file_with_several_types_includes_all_of_them(self):
        code = """
        interface Shape {
            double area();
        }

        class Square implements Shape {
            public double area() { return 1; }
        }
        """
        file = ReviewFile('./', '', 'Shapes.java', contents=code)

        graph = build_java_graph([file])

        types = {(entity.type, entity.info['name'])
                 for entity in graph['entities']}
        self.assertEqual(types, {('interface', 'Shape'),
                                 ('abstractMethod', 'area'),
                                 ('class', 'Square'), ('method', 'area')})

    def test_file_without_types_builds_empty_graph(self):
        file = ReviewFile('./', '', 'Empty.java', contents='')

        graph = build_java_graph([file])

        self.assertEqual(graph['entities'], [])


if __name__ == '__main__':
    unittest.main()
