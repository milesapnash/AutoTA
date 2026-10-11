from src.entity_relations import er_classes

# The relations that an entity in the graph can have with another
RELATIONS = set(er_classes.Entity().relations)


def as_list(targets):
    return [targets] if isinstance(targets, str) else list(targets)


class Role:
    """A role in a pattern, written much as the declaration that fills it
    would be: with its name, then the roles of its members, then its
    relations to other roles, such as implements='strategy'. The relations
    that it must not have are given as never."""
    entity_type = None

    def __init__(self, name, *members, modifiers=(), never=None,
                 **relations):
        never = never or {}
        unknown = (set(relations) | set(never)) - RELATIONS
        if unknown:
            raise TypeError(f'Unknown relations for {name}: {unknown}')
        self.name = name
        self.members = members
        self.modifiers = set(modifiers)
        self.relations = relations
        self.never = never


class Class(Role):
    entity_type = er_classes.Class


class AbstractClass(Role):
    entity_type = er_classes.AbstractClass


class Interface(Role):
    entity_type = er_classes.Interface


class Constructor(Role):
    entity_type = er_classes.Constructor


class Method(Role):
    entity_type = er_classes.Method


class AbstractMethod(Role):
    entity_type = er_classes.AbstractMethod


class Field(Role):
    entity_type = er_classes.Field


class Pattern:
    """A pattern, written as a skeleton of the code that implements it. It
    is made up of the entity that fills each of its roles, the relations
    that there must be between the roles, and the relations that there must
    not be. A role has its members, and the first role is the one that each
    instance of the pattern is found from."""

    def __init__(self, *roles):
        self.roles = {}
        self.relations = {}
        self.forbidden = {}
        for role in roles:
            self.add(role)

        for relations in (self.relations, self.forbidden):
            unknown = {target for role_relations in relations.values()
                       for targets in role_relations.values()
                       for target in targets} - set(self.roles)
            if unknown:
                raise ValueError(f'Relations with unknown roles: {unknown}')

    def add(self, role):
        if role.name in self.roles:
            raise ValueError(f'Two roles are named {role.name}')
        info = {'modifiers': role.modifiers} if role.modifiers else None
        self.roles[role.name] = role.entity_type(info=info)

        relations = {relation: as_list(targets)
                     for relation, targets in role.relations.items()}
        if role.members:
            relations['has'] = [member.name for member in role.members]
        if relations:
            self.relations[role.name] = relations
        if role.never:
            self.forbidden[role.name] = {
                relation: as_list(targets)
                for relation, targets in role.never.items()}

        for member in role.members:
            self.add(member)


# A class with a single instance, which is reached through the class itself
SINGLETON = Pattern(
    Class('singleton',
          Constructor('private constructor', modifiers={'private'}),
          Field('private instance', modifiers={'private'},
                isOfType='singleton', instantiates='singleton'),
          Method('get_instance', hasReturnType='singleton',
                 returns='private instance')))

# A method that sets out the steps of an algorithm, leaving some of them for
# subclasses to fill in
TEMPLATE_METHOD = Pattern(
    AbstractClass('template',
                  AbstractMethod('abstract method'),
                  Method('template method', invokes='abstract method')),
    Class('subclass',
          Method('override', overrides='abstract method'),
          extends='template'))

# A family of interchangeable algorithms behind one interface, held by the
# class that uses them
STRATEGY = Pattern(
    Class('context',
          Field('context_field', isOfType='strategy'),
          Method('context_method', invokes='strategy_method'),
          # A class that implements the interface it holds is combining or
          # wrapping its own kind, as a composite or a decorator does
          never={'implements': 'strategy'}),
    Interface('strategy',
              AbstractMethod('strategy_method')),
    Class('concrete_strategy', implements='strategy'),
    Method('concrete_method', overrides='strategy_method'))

# Creational patterns

# A factory interface for making families of related products, with a factory
# for each family
ABSTRACT_FACTORY = Pattern(
    Interface('factory',
              AbstractMethod('create_a', hasReturnType='product_a'),
              AbstractMethod('create_b', hasReturnType='product_b')),
    Interface('product_a'),
    Interface('product_b'),
    Class('concrete_factory',
          Method('concrete_create_a', overrides='create_a',
                 instantiates='concrete_product_a'),
          Method('concrete_create_b', overrides='create_b',
                 instantiates='concrete_product_b'),
          implements='factory'),
    Class('concrete_product_a', implements='product_a'),
    Class('concrete_product_b', implements='product_b'))

# A creator that leaves the class of the product it uses for its subclasses to
# choose
FACTORY_METHOD = Pattern(
    AbstractClass('creator',
                  AbstractMethod('factory_method', hasReturnType='product'),
                  Method('operation', invokes='factory_method')),
    Interface('product'),
    Class('concrete_creator',
          Method('concrete_factory_method', overrides='factory_method',
                 instantiates='concrete_product'),
          extends='creator'),
    Class('concrete_product', implements='product'))

# A director that puts a product together step by step, through a builder
# interface
BUILDER = Pattern(
    Class('director',
          Field('director_field', isOfType='builder'),
          Method('construct', invokes=['build_step', 'get_result'])),
    Interface('builder',
              AbstractMethod('build_step'),
              AbstractMethod('get_result', hasReturnType='product')),
    Class('product',
          Method('product_method')),
    Class('concrete_builder',
          Field('product_field', isOfType='product', instantiates='product'),
          Method('concrete_step', overrides='build_step',
                 invokes='product_method'),
          Method('concrete_get_result', overrides='get_result',
                 returns='product_field'),
          implements='builder'))

# New objects made by copying an existing one
PROTOTYPE = Pattern(
    Interface('prototype',
              AbstractMethod('copy', hasReturnType='prototype')),
    Class('concrete_prototype',
          Method('concrete_copy', overrides='copy',
                 instantiates='concrete_prototype'),
          implements='prototype'),
    Method('client', invokes='copy'))

# Structural patterns

# A class that gives another class the interface that is expected of it
ADAPTER = Pattern(
    Interface('target',
              AbstractMethod('target_method')),
    Class('adapter',
          Field('adaptee_field', isOfType='adaptee'),
          Method('adapter_method', overrides='target_method',
                 invokes='adaptee_method'),
          implements='target'),
    Class('adaptee',
          Method('adaptee_method'),
          # A class that already implements the target has no need of an
          # adapter, and one that stands in for it is a proxy
          never={'implements': 'target'}))

# An abstraction that holds its implementation behind an interface, so that the
# two can vary separately
BRIDGE = Pattern(
    AbstractClass('abstraction',
                  Field('implementor_field', isOfType='implementor'),
                  AbstractMethod('abstract_operation')),
    Interface('implementor',
              AbstractMethod('implementor_method')),
    Class('refined_abstraction',
          Method('refined_operation', overrides='abstract_operation',
                 invokes='implementor_method'),
          extends='abstraction'),
    Class('concrete_implementor', implements='implementor'))

# A component that holds others of its own kind, so that a group can be treated
# as one
COMPOSITE = Pattern(
    Interface('component',
              AbstractMethod('operation')),
    Class('leaf', implements='component'),
    Class('composite',
          Field('children', isCollectionOf='component'),
          Method('add', parameterOfType='component'),
          Method('composite_operation', overrides='operation',
                 invokes='operation'),
          implements='component'))

# A wrapper that adds behaviour to a component while keeping its interface
DECORATOR = Pattern(
    Interface('component',
              AbstractMethod('operation')),
    Class('concrete_component', implements='component'),
    AbstractClass('decorator',
                  Field('wrapped', isOfType='component'),
                  implements='component'),
    Class('concrete_decorator',
          Method('decorated_operation', overrides='operation',
                 invokes='operation'),
          extends='decorator'))

# One class that gives a simple way into several subsystem classes
FACADE = Pattern(
    Class('facade',
          Field('subsystem_field_a', isOfType='subsystem_a'),
          Field('subsystem_field_b', isOfType='subsystem_b'),
          Method('facade_method',
                 invokes=['subsystem_method_a', 'subsystem_method_b'])),
    Class('subsystem_a',
          Method('subsystem_method_a')),
    Class('subsystem_b',
          Method('subsystem_method_b')))

# Shared objects handed out by a factory that keeps a pool of them
FLYWEIGHT = Pattern(
    Interface('flyweight',
              AbstractMethod('operation')),
    Class('concrete_flyweight',
          Field('intrinsic_state'),
          implements='flyweight'),
    Class('flyweight_factory',
          Field('pool', isCollectionOf='flyweight'),
          Method('get_flyweight', hasReturnType='flyweight',
                 instantiates='concrete_flyweight')))

# A stand-in that controls access to the real object behind the same interface
PROXY = Pattern(
    Interface('subject',
              AbstractMethod('subject_method')),
    Class('real_subject',
          Method('real_method', overrides='subject_method'),
          implements='subject'),
    Class('proxy',
          Field('real_field', isOfType='real_subject'),
          Method('proxy_method', overrides='subject_method',
                 invokes='real_method'),
          implements='subject'))

# Behavioural patterns

# Handlers linked in a chain, each passing a request on to the next
CHAIN_OF_RESPONSIBILITY = Pattern(
    AbstractClass('handler',
                  Field('next_handler', isOfType='handler'),
                  # The request is passed along the chain by handle invoking
                  # itself on the next handler
                  Method('handle', invokes=['handle', 'abstract_step']),
                  AbstractMethod('abstract_step')),
    Class('concrete_handler',
          Method('concrete_step', overrides='abstract_step'),
          extends='handler'))

# A request held as an object, which an invoker runs without knowing what it
# does
COMMAND = Pattern(
    Interface('command',
              AbstractMethod('execute')),
    Class('concrete_command',
          Field('receiver_field', isOfType='receiver'),
          Method('concrete_execute', overrides='execute',
                 invokes='receiver_method'),
          implements='command'),
    Class('receiver',
          Method('receiver_method')),
    Class('invoker',
          Method('add_command', parameterOfType='command'),
          Method('invoke', invokes='execute')))

# A grammar whose rules are classes that interpret themselves against a context
INTERPRETER = Pattern(
    Interface('expression',
              AbstractMethod('interpret', parameterOfType='context')),
    Class('context'),
    Class('terminal', implements='expression'),
    Class('nonterminal',
          Field('child_field', isOfType='expression'),
          Method('nonterminal_interpret', overrides='interpret',
                 invokes='interpret'),
          implements='expression'))

# An object that steps through a collection without showing how the collection
# is held
ITERATOR = Pattern(
    Interface('iterator',
              AbstractMethod('has_next'),
              AbstractMethod('next_item')),
    Interface('aggregate',
              AbstractMethod('create_iterator', hasReturnType='iterator')),
    Class('concrete_iterator', implements='iterator'),
    Class('concrete_aggregate',
          Method('concrete_create_iterator', overrides='create_iterator',
                 instantiates='concrete_iterator'),
          implements='aggregate'))

# Colleagues that talk through a mediator rather than to each other
MEDIATOR = Pattern(
    Interface('mediator',
              AbstractMethod('relay', parameterOfType='colleague')),
    AbstractClass('colleague',
                  Field('mediator_field', isOfType='mediator'),
                  Method('send', invokes='relay'),
                  AbstractMethod('receive')),
    Class('concrete_mediator',
          Method('concrete_relay', overrides='relay', invokes='receive'),
          implements='mediator'),
    Class('concrete_colleague', extends='colleague'))

# An object's state saved outside it, so that it can be put back later
MEMENTO = Pattern(
    Class('originator',
          Field('originator_state'),
          Method('save', hasReturnType='memento', instantiates='memento'),
          Method('restore', parameterOfType='memento', invokes='get_state',
                 assigns='originator_state')),
    Class('memento',
          Field('state'),
          Method('get_state', returns='state')),
    Class('caretaker',
          Method('store', parameterOfType='memento'),
          Method('retrieve', hasReturnType='memento')))

# A subject that tells its observers when it changes
OBSERVER = Pattern(
    Class('subject',
          Field('observers', isCollectionOf='observer'),
          Method('attach', parameterOfType='observer'),
          Method('notify', invokes='update'),
          # A class that holds others of its own kind is a composite
          never={'implements': 'observer'}),
    Interface('observer',
              AbstractMethod('update')),
    Class('concrete_observer', implements='observer'))

# A context that leaves its behaviour to an object for the state it is in,
# which changes as it goes
STATE = Pattern(
    Class('context',
          Field('state_field', isOfType='state'),
          Method('set_state', parameterOfType='state', assigns='state_field'),
          Method('request', invokes='handle')),
    Interface('state',
              AbstractMethod('handle', parameterOfType='context')),
    Class('concrete_state', implements='state'),
    Method('transition', instantiates='next_state'),
    Class('next_state', implements='state'))

# An operation over a set of element classes, held in a visitor that each
# element accepts
VISITOR = Pattern(
    Interface('element',
              AbstractMethod('accept', parameterOfType='visitor')),
    Interface('visitor',
              AbstractMethod('visit_a', parameterOfType='concrete_element_a'),
              AbstractMethod('visit_b', parameterOfType='concrete_element_b')),
    Class('concrete_element_a',
          Method('accept_a', overrides='accept', invokes='visit_a'),
          implements='element'),
    Class('concrete_element_b',
          Method('accept_b', overrides='accept', invokes='visit_b'),
          implements='element'),
    Class('concrete_visitor', implements='visitor'))

# Python has no private constructors and its types are optional, so a Singleton
# is a class holding a private class attribute that is reached through a static
# method, a class method or __new__
PYTHON_SINGLETON = Pattern(
    Class('singleton',
          Field('private instance', modifiers={'private', 'static'},
                instantiates='singleton'),
          Method('get_instance', modifiers={'static'},
                 returns='private instance')))

PATTERNS = {'singleton': SINGLETON,
            'templateMethod': TEMPLATE_METHOD,
            'strategy': STRATEGY,
            'abstractFactory': ABSTRACT_FACTORY,
            'factoryMethod': FACTORY_METHOD,
            'builder': BUILDER,
            'prototype': PROTOTYPE,
            'adapter': ADAPTER,
            'bridge': BRIDGE,
            'composite': COMPOSITE,
            'decorator': DECORATOR,
            'facade': FACADE,
            'flyweight': FLYWEIGHT,
            'proxy': PROXY,
            'chainOfResponsibility': CHAIN_OF_RESPONSIBILITY,
            'command': COMMAND,
            'interpreter': INTERPRETER,
            'iterator': ITERATOR,
            'mediator': MEDIATOR,
            'memento': MEMENTO,
            'observer': OBSERVER,
            'state': STATE,
            'visitor': VISITOR}

# The patterns above are general, and are used for every language. A pattern is
# only redefined for a language here when the general definition cannot apply
# to it.
LANGUAGE_OVERRIDES = {('singleton', 'python'): PYTHON_SINGLETON}


def pattern_library(pattern, language=None):
    """Returns the definition of a pattern for a language, or None if there
    is no pattern of that name."""
    return LANGUAGE_OVERRIDES.get((pattern, language), PATTERNS.get(pattern))
