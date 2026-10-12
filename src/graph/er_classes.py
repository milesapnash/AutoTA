# The relation that each relation is recorded as on the entity it leads to
INVERSES = {
    'has': 'memberOf',
    'extends': 'extendedBy',
    'implements': 'implementedBy',
    'instantiates': 'instantiatedBy',
    'overrides': 'overriddenBy',
    'invokes': 'invokedBy',
    'parameterOfType': 'typeOfParameter',
    'isOfType': 'isTypeOf',
    'isCollectionOf': 'isElementTypeOf',
    'hasReturnType': 'isReturnTypeOf',
    'assigns': 'assignedBy',
    'returns': 'returnedBy',
}


class Entity:
    types = {'class', 'abstractClass', 'interface', 'constructor', 'method',
             'abstractMethod', 'field'}

    def __init__(self, entity_type='entity', info=None, node=None,
                 package=None, file=None):
        self.type = entity_type
        self.info = info
        self.node = node
        self.package = package
        self.file = file
        self.relations = {name: [] for pair in INVERSES.items()
                          for name in pair}

    def __str__(self):
        if self.info is None or self.info["name"] is None:
            return f'{self.type}'
        return f'{self.file} : {self.type}: {self.info["name"]}'

    def __repr__(self):
        if self.info is None or self.info["name"] is None:
            return f'{self.type}'
        return f'{self.file} : {self.type}: {self.info["name"]}'


class Class(Entity):
    def __init__(self, info=None, node=None, package=None, file=None):
        super().__init__('class', info, node, package, file)


class AbstractClass(Entity):
    def __init__(self, info=None, node=None, package=None, file=None):
        super().__init__('abstractClass', info, node, package, file)


class Interface(Entity):
    def __init__(self, info=None, node=None, package=None, file=None):
        super().__init__('interface', info, node, package, file)


class Constructor(Entity):
    def __init__(self, info=None, node=None, package=None, file=None):
        super().__init__('constructor', info, node, package, file)


class Method(Entity):
    def __init__(self, info=None, node=None, package=None, file=None):
        super().__init__('method', info, node, package, file)


class AbstractMethod(Entity):
    def __init__(self, info=None, node=None, package=None, file=None):
        super().__init__('abstractMethod', info, node, package, file)


class Field(Entity):
    def __init__(self, info=None, node=None, package=None, file=None):
        super().__init__('field', info, node, package, file)


class Relation:
    """A relation from one entity to another, which is also recorded on both
    of them: as itself on the source and as its inverse on the target."""
    relation_type = None

    def __init__(self, source, target):
        self.source = source
        self.target = target
        source.relations[self.relation_type].append(target)
        target.relations[INVERSES[self.relation_type]].append(source)

    def __str__(self):
        return f'{self.source} {self.relation_type} {self.target}'

    def __repr__(self):
        return f'{self.source} {self.relation_type} {self.target}'


class Has(Relation):
    relation_type = 'has'


class Implements(Relation):
    relation_type = 'implements'


class Extends(Relation):
    relation_type = 'extends'


class ParameterOfType(Relation):
    relation_type = 'parameterOfType'


class IsOfType(Relation):
    relation_type = 'isOfType'


class HasReturnType(Relation):
    relation_type = 'hasReturnType'


class Invokes(Relation):
    relation_type = 'invokes'


class Overrides(Relation):
    relation_type = 'overrides'


class Instantiates(Relation):
    relation_type = 'instantiates'


class IsCollectionOf(Relation):
    relation_type = 'isCollectionOf'


class Assigns(Relation):
    relation_type = 'assigns'


class Returns(Relation):
    relation_type = 'returns'
