from src.scope import in_scope


class Rule:
    def __init__(self, scope='project'):
        self.scope = scope

    def file_filter(self, file):
        if self.scope == 'project':
            return file.ast

        scope_type, scope = self.scope
        if scope_type == 'dir':
            if in_scope(file.relative_dir, scope):
                return file.ast
            else:
                return None

        if scope_type == 'file':
            if file.file_name == scope:
                return file.ast
            else:
                return None

        print('Invalid scope given')
        return file.ast

    def applies_to(self, language):
        return True

    def apply(self, review_file):
        raise NotImplementedError

    def passed_message(self):
        """The feedback to give when nothing breaks the rule."""
        raise NotImplementedError
