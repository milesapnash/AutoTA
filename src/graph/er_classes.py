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
    type = 'entity'

    def __init__(self, *, name=None, modifiers=(), node=None, package=None,
                 file=None, declared_type=None, supertype=None):
        self.name = name
        self.modifiers = set(modifiers)
        self.node = node
        self.package = package
        self.file = file
        # The name of the type that a field is declared with
        self.declared_type = declared_type
        # The name of the type that an anonymous class extends or implements
        self.supertype = supertype
        self.relations = {relation: [] for pair in INVERSES.items()
                          for relation in pair}

    def __str__(self):
        if self.name is None:
            return f'{self.type}'
        return f'{self.file} : {self.type}: {self.name}'

    __repr__ = __str__


class Class(Entity):
    type = 'class'


class AbstractClass(Entity):
    type = 'abstractClass'


class Interface(Entity):
    type = 'interface'


class Constructor(Entity):
    type = 'constructor'


class Method(Entity):
    type = 'method'


class AbstractMethod(Entity):
    type = 'abstractMethod'


class Field(Entity):
    type = 'field'


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
