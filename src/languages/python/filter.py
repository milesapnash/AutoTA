import ast

from src.languages.base_filter import Filter

FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)
ASSIGNMENTS = (ast.Assign, ast.AnnAssign)
ENUM_BASES = {'Enum', 'IntEnum', 'StrEnum', 'Flag', 'IntFlag'}
KINDS = {'node', 'class', 'interface', 'enum', 'method', 'constructor',
         'field', 'method_invocation'}


def identifier(node):
    """Returns the rightmost name in an expression such as abc.ABC."""
    if isinstance(node, ast.Call):
        node = node.func
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def base_names(node):
    return [identifier(base) for base in node.bases]


def decorator_names(node):
    return [identifier(decorator) for decorator in node.decorator_list]


def is_abstract_method(node):
    return 'abstractmethod' in decorator_names(node)


def is_abstract_class(node):
    metaclasses = [identifier(keyword.value) for keyword in node.keywords
                   if keyword.arg == 'metaclass']
    return 'ABC' in base_names(node) or 'ABCMeta' in metaclasses


def class_kind(node):
    """Python has no interfaces, so a Protocol, or an abstract class whose
    methods are all abstract, is treated as one."""
    bases = set(base_names(node))
    if bases & ENUM_BASES:
        return 'enum'
    if 'Protocol' in bases:
        return 'interface'
    methods = [member for member in node.body
               if isinstance(member, FUNCTIONS)]
    if is_abstract_class(node) and methods and all(
            is_abstract_method(method) for method in methods):
        return 'interface'
    return 'class'


def assignment_targets(node):
    return node.targets if isinstance(node, ast.Assign) else [node.target]


def is_field(node, in_method):
    """A field is assigned to a name in a class body, or to an attribute of
    self within a method."""
    for target in assignment_targets(node):
        if in_method:
            if (isinstance(target, ast.Attribute)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == 'self'):
                return True
        elif isinstance(target, ast.Name):
            return True
    return False


def classify(tree):
    """Yields a (kind, node, owner) triple for every node in the tree, where
    owner is the class that a constructor, method, field or nested class
    belongs to.
    Python's AST does not distinguish constructors from methods or fields
    from local variables, so a node's kind depends on where it appears."""
    seen_fields = set()

    def visit(node, owner, in_method):
        kind = 'node'
        member_of = None
        child_owner, child_in_method = owner, in_method
        if isinstance(node, ast.ClassDef):
            kind = class_kind(node)
            # A nested class belongs to the class it is declared within
            member_of = owner
            child_owner, child_in_method = node, False
        elif isinstance(node, FUNCTIONS):
            is_member = owner is not None and not in_method
            kind = ('constructor' if is_member and node.name == '__init__'
                    else 'method')
            member_of = owner if is_member else None
            child_in_method = owner is not None
        elif (isinstance(node, ASSIGNMENTS) and owner is not None
              and is_field(node, in_method)):
            # A field assigned in several places is only reported once
            key = (id(owner), PythonFilter.name_of(node))
            if key not in seen_fields:
                seen_fields.add(key)
                kind = 'field'
                member_of = owner
        elif isinstance(node, ast.Call):
            kind = 'method_invocation'

        yield kind, node, member_of
        for child in ast.iter_child_nodes(node):
            yield from visit(child, child_owner, child_in_method)

    yield from visit(tree, None, False)


class PythonFilter(Filter):
    language = 'python'
    node_classes = KINDS

    @staticmethod
    def name_of(node):
        if isinstance(node, ASSIGNMENTS):
            return identifier(assignment_targets(node)[0])
        if hasattr(node, 'name'):
            return node.name
        return identifier(node)

    @staticmethod
    def line_of(node):
        return node.lineno

    @staticmethod
    def modifiers_of(node):
        """Python has no access modifiers, so a leading underscore is taken
        to mean private. Class attributes, static or class methods and
        __new__ are static."""
        name = PythonFilter.name_of(node) or ''
        is_dunder = name.startswith('__') and name.endswith('__')
        modifiers = {'private' if name.startswith('_') and not is_dunder
                     else 'public'}

        if isinstance(node, ast.ClassDef):
            if is_abstract_class(node):
                modifiers.add('abstract')
        elif isinstance(node, FUNCTIONS):
            decorators = decorator_names(node)
            if 'abstractmethod' in decorators:
                modifiers.add('abstract')
            if (node.name == '__new__' or 'staticmethod' in decorators
                    or 'classmethod' in decorators):
                modifiers.add('static')
        elif isinstance(node, ASSIGNMENTS):
            if isinstance(assignment_targets(node)[0], ast.Name):
                modifiers.add('static')
        return modifiers

    def _filter_node_class(self, node, kind):
        return self.node_class in ('node', kind)

    @staticmethod
    def has_modifiers(node):
        return isinstance(node, (ast.ClassDef,) + FUNCTIONS + ASSIGNMENTS)

    @staticmethod
    def annotations_of(node):
        if not hasattr(node, 'decorator_list'):
            return None
        return decorator_names(node)

    @staticmethod
    def extended_types(node):
        return base_names(node) if isinstance(node, ast.ClassDef) else None

    # Python does not tell the types that a class extends from those that
    # it implements
    implemented_types = extended_types

    @staticmethod
    def type_of(node):
        if not isinstance(node, ast.AnnAssign):
            return None
        return identifier(node.annotation)

    @staticmethod
    def return_type_of(node):
        if not isinstance(node, FUNCTIONS) or node.returns is None:
            return None
        return identifier(node.returns)

    def get_nodes(self, tree):
        return [node for kind, node, _ in classify(tree)
                if self._passes_filter(node, kind)]
