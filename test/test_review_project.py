import os
import tempfile
import unittest

from src.filters.java_filter import JavaFilter
from src.project.review_file import ReviewFile
from src.project.review_project import ReviewProject
from src.project.spec import Spec, build_spec
from src.rules.identifier_rule import IdentifierRule

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
