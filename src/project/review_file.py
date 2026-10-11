import os

from src.languages import LANGUAGES, language_of


class ReviewFile:

    def __init__(self, root, relative_path, file_name, contents=None):
        self.root = root
        self.relative_path = relative_path
        self.file_name = file_name
        self.feedback = []

        if contents is None:
            with open(os.path.join(root, file_name), 'r', encoding='utf-8',
                      errors='replace') as file:
                self.contents = file.read()
        else:
            self.contents = contents

        self.language = language_of(file_name)

        if self.language is not None:
            self.ast = LANGUAGES[self.language].parse(self.contents)
        else:
            self.ast = None
