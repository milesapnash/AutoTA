import os

from src.languages import LANGUAGES, language_of


class ReviewFile:

    def __init__(self, root, relative_dir, file_name, contents=None):
        self.relative_dir = relative_dir
        self.file_name = file_name
        self.feedback = []
        # Why the file could not be reviewed, if it could not be
        self.error = None
        self.ast = None

        if contents is None:
            try:
                with open(os.path.join(root, file_name), 'r',
                          encoding='utf-8', errors='replace') as file:
                    self.contents = file.read()
            except OSError as error:
                self.contents = ''
                self.error = f'could not be read ({error.strerror})'
        else:
            self.contents = contents

        self.language = language_of(file_name)

        if self.language is not None and self.error is None:
            try:
                self.ast = LANGUAGES[self.language].parse(self.contents)
            except SyntaxError as error:
                where = f'line {error.lineno}: ' if error.lineno else ''
                self.error = f'could not be parsed ({where}{error.msg})'
            except (ValueError, RecursionError) as error:
                self.error = f'could not be parsed ({error})'
