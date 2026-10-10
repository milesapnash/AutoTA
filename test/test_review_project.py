import os
import tempfile
import unittest

from src.filters.java_filter import JavaFilter
from src.project.review_file import ReviewFile
from src.project.review_project import ReviewProject
from src.project.spec import Spec
from src.rules.identifier_rule import IdentifierRule

PATTERN_REPOS = os.path.join(os.path.dirname(__file__), 'pattern_repos')


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

    def test_rule_ignores_files_in_another_language(self):
        code = 'class Example:\n    def testThing(self):\n        pass\n'
        file = ReviewFile('./', '', 'example.py', contents=code)
        rule = IdentifierRule(node_filter=JavaFilter(node_class='method',
                                                     node_name=r'^test'))

        self.assertEqual(rule.apply(file), [])


if __name__ == '__main__':
    unittest.main()
