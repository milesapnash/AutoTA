# The relation that each relation is recorded as on the entity it leads to
INVERSES = {'has': 'composes', 'extends': 'extendedBy',
            'implements': 'implementedBy', 'instantiates': 'instantiatedBy',
            'overrides': 'overriddenBy', 'invokes': 'invokedBy',
            'parameterOfType': 'typeOfParameter', 'isOfType': 'isTypeOf',
            'isCollectionOf': 'isElementTypeOf',
            'hasReturnType': 'isReturnTypeOf', 'assigns': 'assignedBy',
            'returns': 'returnedBy'}


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
        self.relations = {'has': [], 'composes': [],
                          'extends': [], 'extendedBy': [],
                          'implements': [], 'implementedBy': [],
                          'instantiates': [], 'instantiatedBy': [],
                          'overrides': [], 'overriddenBy': [],
                          'invokes': [], 'invokedBy': [],
                          'parameterOfType': [], 'typeOfParameter': [],
                          'isOfType': [], 'isTypeOf': [],
                          'isCollectionOf': [], 'isElementTypeOf': [],
                          'hasReturnType': [], 'isReturnTypeOf': [],
                          'assigns': [], 'assignedBy': [],
                          'returns': [], 'returnedBy': []}

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
    def __init__(self, source, target, relation_type):
        self.source = source
        self.target = target
        self.relation_type = relation_type

    def __str__(self):
        return f'{self.source} {self.relation_type} {self.target}'

    def __repr__(self):
        return f'{self.source} {self.relation_type} {self.target}'


class Has(Relation):
    def __init__(self, source, target):
        super().__init__(source, target, 'has')
        source.relations['has'].append(target)
        target.relations['composes'].append(source)


class Implements(Relation):
    def __init__(self, source, target):
        super().__init__(source, target, 'implements')
        source.relations['implements'].append(target)
        target.relations['implementedBy'].append(source)


class Extends(Relation):
    def __init__(self, source, target):
        super().__init__(source, target, 'extends')
        source.relations['extends'].append(target)
        target.relations['extendedBy'].append(source)


class ParameterOfType(Relation):
    def __init__(self, source, target):
        super().__init__(source, target, 'parameterOfType')
        source.relations['parameterOfType'].append(target)
        target.relations['typeOfParameter'].append(source)


class IsOfType(Relation):
    def __init__(self, source, target):
        super().__init__(source, target, 'isOfType')
        source.relations['isOfType'].append(target)
        target.relations['isTypeOf'].append(source)


class HasReturnType(Relation):
    def __init__(self, source, target):
        super().__init__(source, target, 'hasReturnType')
        source.relations['hasReturnType'].append(target)
        target.relations['isReturnTypeOf'].append(source)


class Invokes(Relation):
    def __init__(self, source, target):
        super().__init__(source, target, 'invokes')
        source.relations['invokes'].append(target)
        target.relations['invokedBy'].append(source)


class Overrides(Relation):
    def __init__(self, source, target):
        super().__init__(source, target, 'overrides')
        source.relations['overrides'].append(target)
        target.relations['overriddenBy'].append(source)


class Instantiates(Relation):
    def __init__(self, source, target):
        super().__init__(source, target, 'instantiates')
        source.relations['instantiates'].append(target)
        target.relations['instantiatedBy'].append(source)


class IsCollectionOf(Relation):
    def __init__(self, source, target):
        super().__init__(source, target, 'isCollectionOf')
        source.relations['isCollectionOf'].append(target)
        target.relations['isElementTypeOf'].append(source)


class Assigns(Relation):
    def __init__(self, source, target):
        super().__init__(source, target, 'assigns')
        source.relations['assigns'].append(target)
        target.relations['assignedBy'].append(source)


class Returns(Relation):
    def __init__(self, source, target):
        super().__init__(source, target, 'returns')
        source.relations['returns'].append(target)
        target.relations['returnedBy'].append(source)
