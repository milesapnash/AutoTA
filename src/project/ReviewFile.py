import os

import javalang as java_ast


def parse_java(contents):
    tokens = list(java_ast.tokenizer.tokenize(contents))
    return java_ast.parser.Parser(tokens).parse()


# To support another language, register its file extension, name and parser
LANGUAGES = {'.java': ('java', parse_java)}


class ReviewFile:

    def __init__(self, root, relative_path, file_name, contents=None):
        self.root = root
        self.relative_path = relative_path
        self.file_name = file_name
        self.feedback = []

        if contents is None:
            with open(os.path.join(root, file_name), 'r') as file:
                self.contents = file.read()
        else:
            self.contents = contents

        extension = os.path.splitext(file_name)[1]

        if extension in LANGUAGES:
            self.language, parse = LANGUAGES[extension]
            self.ast = parse(self.contents)
        else:
            self.ast = None
