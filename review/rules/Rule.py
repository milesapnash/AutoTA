import os


class Rule:
    def __init__(self, scope='project'):
        self.scope = scope

    def filter(self, file):
        if self.scope == 'project':
            return file.ast

        scope_type, scope = self.scope
        if scope_type == 'dir':
            directory_path = os.path.normpath(scope)
            if os.path.commonpath(
                    [os.path.normpath(file.root),
                     directory_path]) == directory_path:
                return file.ast
            else:
                return None

        if scope_type == 'file':
            if file.file_name == scope:
                return file.ast
            else:
                return None

        print('ERROR')
        return Exception

    def apply(self, review_file):
        return NotImplementedError
