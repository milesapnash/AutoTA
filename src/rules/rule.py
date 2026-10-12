from src.scope import in_scope


class Rule:
    def __init__(self, scope='.'):
        # The directory that the rule applies to, given as it is to in_scope
        self.scope = scope

    def file_filter(self, file):
        return file.ast if in_scope(file.relative_dir, self.scope) else None

    def scope_name(self):
        """How the scope is named in feedback."""
        return 'the project' if in_scope('.', self.scope) else self.scope

    def applies_to(self, language):
        return True

    def apply(self, review_file):
        raise NotImplementedError

    def passed_message(self):
        """The feedback to give when nothing breaks the rule."""
        raise NotImplementedError
