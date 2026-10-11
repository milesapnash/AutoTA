import ast
import re

from src.filters.base_filter import Filter

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
    def __init__(self, negatives=None, node_class='node', node_name=None,
                 node_modifiers=None,
                 node_annotations=None, node_extends=None,
                 node_implements=None,
                 node_type=None, node_return_type=None):
        super().__init__('python')
        if node_class not in KINDS:
            raise ValueError(f'Unknown node class: {node_class}')

        self.node_class = node_class
        self.node_name = node_name
        self.node_modifiers = node_modifiers
        self.node_annotations = node_annotations
        self.node_extends = node_extends
        self.node_implements = node_implements
        self.node_type = node_type
        self.node_return_type = node_return_type
        self.negatives = negatives

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

    def _filter_node_class(self, kind):
        return self.node_class in ('node', kind)

    def _filter_node_name(self, node):
        if self.node_name is None:
            return True
        comp_name = self.name_of(node)
        if comp_name is None:
            return False
        return re.match(self.node_name, comp_name)

    def _filter_node_modifiers(self, node):
        if self.node_modifiers is None or len(self.node_modifiers) == 0:
            return True
        if not isinstance(node, (ast.ClassDef,) + FUNCTIONS + ASSIGNMENTS):
            return False

        if self.negatives is None or 'node_modifiers' not in self.negatives:
            return set(self.node_modifiers).issubset(self.modifiers_of(node))
        else:
            return set(self.node_modifiers).isdisjoint(
                self.modifiers_of(node))

    def _filter_node_annotations(self, node):
        if self.node_annotations is None or len(self.node_annotations) == 0:
            return True
        if not hasattr(node, 'decorator_list'):
            return False
        return set(self.node_annotations).issubset(
            set(decorator_names(node)))

    def _filter_node_extends(self, node):
        if self.node_extends is None:
            return True
        if not isinstance(node, ast.ClassDef):
            return False
        return self.node_extends in base_names(node)

    def _filter_node_implements(self, node):
        if self.node_implements is None or len(self.node_implements) == 0:
            return True
        if not isinstance(node, ast.ClassDef):
            return False
        return set(self.node_implements).issubset(set(base_names(node)))

    def _filter_node_type(self, node):
        if self.node_type is None:
            return True
        if not isinstance(node, ast.AnnAssign):
            return False
        return identifier(node.annotation) == self.node_type

    def _filter_node_return_type(self, node):
        if self.node_return_type is None:
            return True
        if not isinstance(node, FUNCTIONS) or node.returns is None:
            return False
        return identifier(node.returns) == self.node_return_type

    def _passes_filter(self, kind, node):
        return all([
            self._filter_node_class(kind),
            self._filter_node_name(node),
            self._filter_node_modifiers(node),
            self._filter_node_annotations(node),
            self._filter_node_extends(node),
            self._filter_node_implements(node),
            self._filter_node_type(node),
            self._filter_node_return_type(node)
        ])

    def get_nodes(self, tree):
        return [node for kind, node, _ in classify(tree)
                if self._passes_filter(kind, node)]
