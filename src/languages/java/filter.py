from src.languages.base_filter import Filter

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
    language = 'java'
    node_classes = NODE_TYPES

    def _filter_node_class(self, node, kind):
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

    @staticmethod
    def has_modifiers(node):
        return node.type.endswith('_declaration')

    modifiers_of = staticmethod(modifiers_of)
    annotations_of = staticmethod(annotations_of)

    @staticmethod
    def extended_types(node):
        return [type_name(supertype) for supertype in supertype_nodes(
            node, 'superclass', 'extends_interfaces')]

    @staticmethod
    def implemented_types(node):
        return [type_name(supertype) for supertype in
                supertype_nodes(node, 'super_interfaces')]

    @staticmethod
    def type_of(node):
        # The type of a method is the type that it returns
        if node.type == 'method_declaration':
            return None
        return type_name(node.child_by_field_name('type'))

    @staticmethod
    def return_type_of(node):
        if node.type != 'method_declaration':
            return None
        return type_name(node.child_by_field_name('type'))

    def get_nodes(self, tree):
        return [node for node in descendants(tree)
                if self._passes_filter(node)]
