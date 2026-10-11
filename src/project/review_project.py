import os
from collections import Counter

from src.languages import LANGUAGES, language_of
from src.project.review_file import ReviewFile
from src.project.utils import create_feedback_pdf, gpt_api_request
from src.rules.encapsulation_rule import EncapsulationRule
from src.rules.identifier_rule import IdentifierRule


class ReviewProject:

    def __init__(self, directory, spec, er_scope=None):
        self.directory = directory
        self.spec = spec
        self.files = []
        self.summary = None
        # The instances found of each design pattern in the spec
        self.pattern_matches = {}

        source_files = [(root, file_name)
                        for root, _, dir_files in os.walk(directory)
                        for file_name in dir_files
                        if language_of(file_name) is not None]
        if not source_files:
            raise ValueError(
                f'No supported source files found in {directory}')

        # The project's language is the one most of its files are written in
        self.language = Counter(
            language_of(file_name) for _, file_name in source_files
        ).most_common(1)[0][0]

        for root, file_name in source_files:
            if language_of(file_name) == self.language:
                self.files.append(
                    ReviewFile(root, os.path.relpath(root, directory),
                               file_name))

        if er_scope is None:
            self.er_graph = self.build_er_graph(self.files)
        else:
            scope_dir = os.path.normpath(er_scope)
            scoped_files = [file for file in self.files if
                            os.path.commonpath(
                                [os.path.normpath(file.relative_path),
                                 scope_dir]) == scope_dir]
            self.er_graph = self.build_er_graph(scoped_files)

        self.feedback = self.get_feedback()

    def get_feedback(self):
        if self.spec is None:
            return []
        feedback = []
        if self.spec.rules is not None:
            feedback = self.apply_rules(self.spec.rules)
        if self.spec.patterns is not None:
            feedback.extend(self.find_patterns(self.spec.patterns))

        return feedback

    def apply_rules(self, rules):
        complete_feedback = ["CODE STYLE RULES:"]
        for rule in rules:
            if not rule.applies_to(self.language):
                continue
            complete_feedback.append(str(rule) + ':')
            rule_feedback = []
            for file in self.files:
                feedback = rule.apply(file)
                if feedback:
                    file.feedback.extend(feedback)
                    rule_feedback.extend(
                        [f'File: {file.file_name}, Line: {line}: {text}' for
                         line, text in feedback])
            if not rule_feedback:
                if isinstance(rule, EncapsulationRule):
                    complete_feedback.append(
                        f'All classes within {rule.scope} were properly '
                        f'encapsulated')
                elif isinstance(rule, IdentifierRule):
                    complete_feedback.append(
                        f'All {rule.node_filter.node_class}s within '
                        f'{rule.scope} had the correct identifier format of '
                        f'{rule.node_filter.node_name}')
            else:
                complete_feedback.extend(rule_feedback)
        complete_feedback.append("")
        return complete_feedback

    def find_patterns(self, patterns):
        pattern_feedback = ["DESIGN PATTERNS:"]
        for pattern in patterns:
            matches = pattern.find_matches(self.er_graph, self.language)
            self.pattern_matches[pattern.pattern] = matches
            pattern_feedback.append('-' + pattern.pattern + '\n' +
                                    pattern.describe(matches))

        return pattern_feedback

    def build_er_graph(self, files):
        return LANGUAGES[self.language].build_graph(files)

    def print_feedback(self):
        if not self.feedback:
            print('User code passes all rules')
        else:
            for feedback in self.feedback:
                print(feedback)

    def get_llm_summary(self):
        self.summary = gpt_api_request(self.files, self.feedback)

    def build_pdf(self, output_path):
        create_feedback_pdf(self.files, self.spec.task, self.summary,
                            output_path)
