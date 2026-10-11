import os
import tempfile
import unittest

from src.filters.java_filter import JavaFilter
from src.project.review_file import ReviewFile
from src.project.review_project import ReviewProject
from src.project.spec import Spec, build_spec
from src.rules.encapsulation_rule import EncapsulationRule
from src.rules.identifier_rule import IdentifierRule
from src.scope import in_scope

TEST_DIR = os.path.dirname(__file__)
PATTERN_REPOS = os.path.join(TEST_DIR, 'pattern_repos')


class TestReviewProject(unittest.TestCase):
    def test_language_is_inferred_from_files(self):
        for language in ('java', 'python'):
            with self.subTest(language=language):
                project = ReviewProject(
                    os.path.join(PATTERN_REPOS, language, 'Strategy'),
                    Spec('language test'))

                self.assertEqual(project.language, language)
                self.assertEqual(len(project.files), 4)

    def test_most_common_language_is_used(self):
        with tempfile.TemporaryDirectory() as directory:
            for file_name in ('A.java', 'B.java', 'script.py'):
                with open(os.path.join(directory, file_name), 'w') as file:
                    file.write('')
            project = ReviewProject(directory, Spec('language test'))

        self.assertEqual(project.language, 'java')
        self.assertEqual({file.file_name for file in project.files},
                         {'A.java', 'B.java'})

    def test_project_without_source_files_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                ReviewProject(directory, Spec('language test'))

    def test_file_is_read_as_utf8(self):
        code = 'class Café { String złoty = "✓"; }'
        with tempfile.TemporaryDirectory() as directory:
            with open(os.path.join(directory, 'Cafe.java'), 'w',
                      encoding='utf-8') as file:
                file.write(code)
            review_file = ReviewFile(directory, '', 'Cafe.java')

        self.assertEqual(review_file.contents, code)

    def test_rule_ignores_files_in_another_language(self):
        code = 'class Example:\n    def testThing(self):\n        pass\n'
        file = ReviewFile('./', '', 'example.py', contents=code)
        rule = IdentifierRule(node_filter=JavaFilter(node_class='method',
                                                     node_name=r'^test'))

        self.assertEqual(rule.apply(file), [])


def write_files(directory, files):
    """Writes each file, given by its path within a directory."""
    for path, contents in files.items():
        full_path = os.path.join(directory, *path.split('/'))
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as file:
            file.write(contents)


MAVEN_PROJECT = {
    'pom.xml': '<project/>',
    'src/main/java/app/Account.java':
        'package app;\npublic class Account { public int balance; }\n',
    'src/test/java/app/AccountTest.java':
        'package app;\npublic class AccountTest { public int count; }\n'}


class TestScope(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = directory.name

    def graph_classes(self, scope):
        project = ReviewProject(self.directory, Spec('scope test'),
                                er_scope=scope)
        return {entity.info['name']
                for entity in project.er_graph['entities']
                if entity.type == 'class'}

    def test_scope_is_found_within_a_maven_layout(self):
        write_files(self.directory, MAVEN_PROJECT)

        for scope in ('main', 'src/main', 'src/main/java/app'):
            with self.subTest(scope=scope):
                self.assertEqual(self.graph_classes(scope), {'Account'})

    def test_scope_of_the_project_directory_is_every_file(self):
        write_files(self.directory, MAVEN_PROJECT)

        for scope in ('.', None):
            with self.subTest(scope=scope):
                self.assertEqual(self.graph_classes(scope),
                                 {'Account', 'AccountTest'})

    def test_scope_with_no_files_is_rejected(self):
        write_files(self.directory, MAVEN_PROJECT)

        with self.assertRaises(ValueError):
            ReviewProject(self.directory, Spec('scope test'),
                          er_scope='missing')

    def test_scope_matches_whole_directory_names(self):
        self.assertTrue(in_scope(os.path.join('src', 'main', 'java'), 'main'))
        self.assertTrue(in_scope('main', 'main'))
        self.assertTrue(in_scope('src/main/java', 'main/java'))
        self.assertFalse(in_scope('src/maintenance', 'main'))
        self.assertFalse(in_scope('src/test/java', 'main'))
        self.assertFalse(in_scope('src/java/main', 'main/java'))
        self.assertFalse(in_scope('.', 'main'))

    def test_rule_scope_is_found_within_a_maven_layout(self):
        write_files(self.directory, MAVEN_PROJECT)
        spec = Spec('scope test',
                    rules=[EncapsulationRule(scope=('dir', 'main'))])

        project = ReviewProject(self.directory, spec)

        self.assertIn('File: Account.java, Line: 2: In class Account, the '
                      'balance field is not private', project.feedback)
        self.assertFalse(any('AccountTest' in line
                             for line in project.feedback))

    def test_rule_with_no_files_in_scope_says_so(self):
        write_files(self.directory, MAVEN_PROJECT)
        spec = Spec('scope test',
                    rules=[EncapsulationRule(scope=('dir', 'missing'))])

        project = ReviewProject(self.directory, spec)

        self.assertIn("No files were found within ('dir', 'missing')",
                      project.feedback)

    def test_directories_that_are_not_source_are_left_out(self):
        write_files(self.directory, {
            'pom.xml': '<project/>',
            'src/app/Kept.java': 'class Kept {}',
            # A package may share its name with a build directory
            'src/app/build/Builder.java': 'class Builder {}',
            'target/generated/Generated.java': 'class Generated {}',
            '.git/hooks/Hook.java': 'class Hook {}',
            'node_modules/lib/Dependency.java': 'class Dependency {}',
            'environment/pyvenv.cfg': '',
            'environment/lib/Installed.java': 'class Installed {}'})

        project = ReviewProject(self.directory, Spec('scope test'))

        self.assertEqual([file.file_name for file in project.files],
                         ['Kept.java', 'Builder.java'])


class TestExampleTasks(unittest.TestCase):
    def review(self, task):
        project = ReviewProject(os.path.join(TEST_DIR, task), build_spec(),
                                er_scope='main')
        return project.feedback

    def test_java_example_task(self):
        feedback = self.review('example_task_java')

        self.assertIn('File: CaesarCipher.java, Line: 5: In class '
                      'CaesarCipher, the cipherShift field is not private',
                      feedback)
        self.assertIn('File: CaesarCipherTest.java, Line: 12: The method, '
                      'testShiftZeroIsSelf, does not follow the specified '
                      'naming convention.', feedback)
        self.assertEqual(feedback.count('-Identifier Rule:'), 1)
        self.assertIn('Found potential instance of templateMethod pattern',
                      feedback[-1])

    def test_python_example_task(self):
        feedback = self.review('example_task_python')

        self.assertIn('File: caesar_cipher.py, Line: 7: In class '
                      'CaesarCipher, the cipher_shift field is not private',
                      feedback)
        self.assertIn('File: caesar_cipher_test.py, Line: 8: The method, '
                      'testShiftZeroIsSelf, does not follow the specified '
                      'naming convention.', feedback)
        self.assertEqual(feedback.count('-Identifier Rule:'), 1)
        self.assertIn('Found potential instance of templateMethod pattern',
                      feedback[-1])


if __name__ == '__main__':
    unittest.main()
