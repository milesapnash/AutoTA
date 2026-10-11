import re

from src.filters.base_filter import Filter

# The type of syntax tree node that each kind of node is parsed as
NODE_TYPES = {'node': None,
              'class': 'class_declaration',
              'method': 'method_declaration',
              'method_invocation': 'method_invocation',
              'field': 'field_declaration',
              'constructor': 'constructor_declaration',
              'interface': 'interface_declaration',
              'enum': 'enum_declaration'}
ANNOTATIONS = ('marker_annotation', 'annotation')


def text(node):
    return node.text.decode() if node is not None else None


def descendants(root):
    """Yields a node and every named node within it."""
    stack = [root]
    while stack:
        node = stack.pop()
        yield node
        stack.extend(reversed(node.named_children))


def child_of_type(node, *node_types):
    for child in node.children:
        if child.type in node_types:
            return child
    return None


def modifier_nodes(node):
    modifiers = child_of_type(node, 'modifiers')
    return modifiers.children if modifiers is not None else []


def modifiers_of(node):
    """Returns the modifiers of a declaration, such as public and static."""
    return {modifier.type for modifier in modifier_nodes(node)
            if modifier.type not in ANNOTATIONS}


def annotations_of(node):
    return [type_name(annotation.child_by_field_name('name'))
            for annotation in modifier_nodes(node)
            if annotation.type in ANNOTATIONS]


def type_name(type_node):
    """Returns the name of a type without its package, type arguments or
    array dimensions, so that java.util.List<String>[] is List."""
    if type_node is None:
        return None
    if type_node.type == 'array_type':
        return type_name(type_node.child_by_field_name('element'))
    if type_node.type in ('generic_type', 'annotated_type',
                          'scoped_type_identifier', 'scoped_identifier'):
        # The name follows any annotations and the scope it is found in,
        # and comes before any type arguments
        names = [child for child in type_node.named_children
                 if child.type not in ANNOTATIONS + ('type_arguments',)]
        return type_name(names[-1]) if names else None
    return text(type_node)


def supertype_nodes(node, *clauses):
    """Returns the types named in the given clauses of a declaration, which
    are superclass, super_interfaces and extends_interfaces."""
    types = []
    for clause in node.children:
        if clause.type not in clauses:
            continue
        for child in clause.named_children:
            # Several supertypes are held in a list
            types.extend(child.named_children if child.type == 'type_list'
                         else [child])
    return types


class JavaFilter(Filter):
    def __init__(self, negatives=None, node_class=None, node_name=None,
                 node_modifiers=None,
                 node_annotations=None, node_extends=None,
                 node_implements=None,
                 node_type=None, node_return_type=None):
        super().__init__('java')

        self.node_class = node_class
        self.node_name = node_name
        self.node_modifiers = node_modifiers
        self.node_annotations = node_annotations
        self.node_extends = node_extends
        self.node_implements = node_implements
        self.node_type = node_type
        self.node_return_type = node_return_type
        self.negatives = negatives

    def _filter_node_class(self, node):
        node_type = NODE_TYPES[self.node_class]
        return node_type is None or node.type == node_type

    @staticmethod
    def name_node(node):
        name = node.child_by_field_name('name')
        if name is None:
            # A field is named by the first variable that it declares
            declarator = node.child_by_field_name('declarator')
            if declarator is not None:
                name = declarator.child_by_field_name('name')
        return name

    @staticmethod
    def name_of(node):
        return text(JavaFilter.name_node(node))

    @staticmethod
    def line_of(node):
        # A declaration starts at its annotations and modifiers, so the
        # line that it is named on is given instead
        name = JavaFilter.name_node(node)
        return (name if name is not None else node).start_point.row + 1

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
        if not node.type.endswith('_declaration'):
            return False

        modifiers = modifiers_of(node)
        if self.negatives is None or 'node_modifiers' not in self.negatives:
            return set(self.node_modifiers).issubset(modifiers)
        else:
            return set(self.node_modifiers).isdisjoint(modifiers)

    def _filter_node_annotations(self, node):
        if self.node_annotations is None or len(self.node_annotations) == 0:
            return True
        return set(self.node_annotations).issubset(set(annotations_of(node)))

    def _filter_node_extends(self, node):
        if self.node_extends is None:
            return True
        extended = supertype_nodes(node, 'superclass', 'extends_interfaces')
        return self.node_extends in [type_name(supertype)
                                     for supertype in extended]

    def _filter_node_implements(self, node):
        if self.node_implements is None or len(self.node_implements) == 0:
            return True
        implemented = [type_name(supertype) for supertype in
                       supertype_nodes(node, 'super_interfaces')]
        return set(self.node_implements).issubset(set(implemented))

    def _filter_node_type(self, node):
        if self.node_type is None:
            return True
        # The type of a method is the type that it returns
        if node.type == 'method_declaration':
            return False
        return type_name(node.child_by_field_name(
            'type')) == self.node_type

    def _filter_node_return_type(self, node):
        if self.node_return_type is None:
            return True
        if node.type != 'method_declaration':
            return False
        return type_name(node.child_by_field_name(
            'type')) == self.node_return_type

    def _passes_filter(self, node):
        return all([
            self._filter_node_class(node),
            self._filter_node_name(node),
            self._filter_node_modifiers(node),
            self._filter_node_annotations(node),
            self._filter_node_extends(node),
            self._filter_node_implements(node),
            self._filter_node_type(node),
            self._filter_node_return_type(node)
        ])

    def get_nodes(self, ast):
        return [node for node in descendants(ast)
                if self._passes_filter(node)]
