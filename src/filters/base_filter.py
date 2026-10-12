import re


class Filter:
    """Selects the nodes of a syntax tree by what they are called, how they
    are declared and what they are related to. A language gives what it has
    of each of these by overriding the methods that follow get_nodes."""
    language = None
    # The kinds of node that can be selected
    node_classes = ()

    def __init__(self, negatives=None, node_class='node', node_name=None,
                 node_modifiers=None, node_annotations=None,
                 node_extends=None, node_implements=None, node_type=None,
                 node_return_type=None):
        if node_class not in self.node_classes:
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

    def get_nodes(self, tree):
        raise NotImplementedError

    def _filter_node_name(self, node):
        if self.node_name is None:
            return True
        comp_name = self.name_of(node)
        if comp_name is None:
            return False
        return re.match(self.node_name, comp_name)

    def _filter_node_modifiers(self, node):
        if not self.node_modifiers:
            return True
        if not self.has_modifiers(node):
            return False

        required = set(self.node_modifiers)
        if self.negatives is not None and 'node_modifiers' in self.negatives:
            return required.isdisjoint(self.modifiers_of(node))
        return required.issubset(self.modifiers_of(node))

    def _filter_node_annotations(self, node):
        if not self.node_annotations:
            return True
        annotations = self.annotations_of(node)
        return (annotations is not None
                and set(self.node_annotations).issubset(annotations))

    def _filter_node_extends(self, node):
        if self.node_extends is None:
            return True
        extended = self.extended_types(node)
        return extended is not None and self.node_extends in extended

    def _filter_node_implements(self, node):
        if not self.node_implements:
            return True
        implemented = self.implemented_types(node)
        return (implemented is not None
                and set(self.node_implements).issubset(implemented))

    def _filter_node_type(self, node):
        if self.node_type is None:
            return True
        return self.type_of(node) == self.node_type

    def _filter_node_return_type(self, node):
        if self.node_return_type is None:
            return True
        return self.return_type_of(node) == self.node_return_type

    def _passes_filter(self, node, kind=None):
        return all([
            self._filter_node_class(node, kind),
            self._filter_node_name(node),
            self._filter_node_modifiers(node),
            self._filter_node_annotations(node),
            self._filter_node_extends(node),
            self._filter_node_implements(node),
            self._filter_node_type(node),
            self._filter_node_return_type(node)
        ])

    def _filter_node_class(self, node, kind):
        raise NotImplementedError

    @staticmethod
    def name_of(node):
        raise NotImplementedError

    @staticmethod
    def line_of(node):
        raise NotImplementedError

    @staticmethod
    def has_modifiers(node):
        """Whether the node is a declaration that has modifiers."""
        raise NotImplementedError

    @staticmethod
    def modifiers_of(node):
        raise NotImplementedError

    @staticmethod
    def annotations_of(node):
        """The names of the annotations of a node, or None if it cannot have
        any."""
        raise NotImplementedError

    @staticmethod
    def extended_types(node):
        """The names of the types that a node extends, or None if it is not
        a type."""
        raise NotImplementedError

    @staticmethod
    def implemented_types(node):
        """The names of the types that a node implements, or None if it is
        not a type."""
        raise NotImplementedError

    @staticmethod
    def type_of(node):
        """The name of the type that a node is declared with, or None."""
        raise NotImplementedError

    @staticmethod
    def return_type_of(node):
        """The name of the type that a method returns, or None."""
        raise NotImplementedError
