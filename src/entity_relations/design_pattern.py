from src.entity_relations.er_classes import (
    AbstractClass, AbstractMethod, Class, Constructor, Field, Interface,
    Method)


def not_none_check(a, b):
    return a is None or a == b


def check_dict(dict_a, dict_b):
    """Checks that every modifier required by dict_a is present in dict_b."""
    if dict_a is None:
        return True
    if dict_b is None:
        return False
    return all(modifier in dict_b.get('modifiers', ())
               for modifier in dict_a.get('modifiers', ()))


def pattern_library(pattern, language=None):
    pattern_dict = {
        'singleton':
            ({
                 'singleton': Class(),
                 'private constructor': Constructor(
                     info={'modifiers': {'private'}}),
                 'private instance': Field(info={'modifiers': {'private'}}),
                 'get_instance': Method()
             },
             {
                 'singleton': {
                     'has': ['private constructor', 'private instance',
                             'get_instance']
                 },
                 'private instance': {
                     'isOfType': ['singleton'],
                     'instantiates': ['singleton']
                 },
                 'get_instance': {
                     'hasReturnType': ['singleton'],
                     'returns': ['private instance']
                 }
             }),
        'templateMethod':
            ({
                 'template': AbstractClass(),
                 'abstract method': AbstractMethod(),
                 'template method': Method(),
                 'subclass': Class(),
                 'override': Method()
             },
             {
                 'template': {
                     'has': ['abstract method', 'template method']
                 },
                 'subclass': {
                     'extends': ['template'],
                     'has': ['override']
                 },
                 'template method': {
                     'invokes': ['abstract method']
                 }
             }),
        'strategy':
            ({
                 'context': Class(),
                 'context_field': Field(),
                 'context_method': Method(),
                 'strategy': Interface(),
                 'strategy_method': AbstractMethod(),
                 'concrete_strategy': Class(),
                 'concrete_method': Method()
             },
             {
                 'context': {
                     'has': ['context_field', 'context_method']
                 },
                 'context_field': {
                     'isOfType': ['strategy']
                 },
                 'context_method': {
                     'invokes': ['strategy_method']
                 },
                 'strategy': {
                     'has': ['strategy_method']
                 },
                 'concrete_strategy': {
                     'implements': ['strategy']
                 },
                 'concrete_method': {
                     'overrides': ['strategy_method']
                 }
             }),

        # Creational patterns
        'abstractFactory':
            ({
                 'factory': Interface(),
                 'create_a': AbstractMethod(),
                 'create_b': AbstractMethod(),
                 'product_a': Interface(),
                 'product_b': Interface(),
                 'concrete_factory': Class(),
                 'concrete_create_a': Method(),
                 'concrete_create_b': Method(),
                 'concrete_product_a': Class(),
                 'concrete_product_b': Class()
             },
             {
                 'factory': {
                     'has': ['create_a', 'create_b']
                 },
                 'create_a': {
                     'hasReturnType': ['product_a']
                 },
                 'create_b': {
                     'hasReturnType': ['product_b']
                 },
                 'concrete_factory': {
                     'implements': ['factory'],
                     'has': ['concrete_create_a', 'concrete_create_b']
                 },
                 'concrete_create_a': {
                     'overrides': ['create_a'],
                     'instantiates': ['concrete_product_a']
                 },
                 'concrete_create_b': {
                     'overrides': ['create_b'],
                     'instantiates': ['concrete_product_b']
                 },
                 'concrete_product_a': {
                     'implements': ['product_a']
                 },
                 'concrete_product_b': {
                     'implements': ['product_b']
                 }
             }),
        'factoryMethod':
            ({
                 'creator': AbstractClass(),
                 'factory_method': AbstractMethod(),
                 'operation': Method(),
                 'product': Interface(),
                 'concrete_creator': Class(),
                 'concrete_factory_method': Method(),
                 'concrete_product': Class()
             },
             {
                 'creator': {
                     'has': ['factory_method', 'operation']
                 },
                 'factory_method': {
                     'hasReturnType': ['product']
                 },
                 'operation': {
                     'invokes': ['factory_method']
                 },
                 'concrete_creator': {
                     'extends': ['creator'],
                     'has': ['concrete_factory_method']
                 },
                 'concrete_factory_method': {
                     'overrides': ['factory_method'],
                     'instantiates': ['concrete_product']
                 },
                 'concrete_product': {
                     'implements': ['product']
                 }
             }),
        'builder':
            ({
                 'director': Class(),
                 'director_field': Field(),
                 'construct': Method(),
                 'builder': Interface(),
                 'build_step': AbstractMethod(),
                 'get_result': AbstractMethod(),
                 'product': Class(),
                 'product_method': Method(),
                 'concrete_builder': Class(),
                 'product_field': Field(),
                 'concrete_step': Method(),
                 'concrete_get_result': Method()
             },
             {
                 'director': {
                     'has': ['director_field', 'construct']
                 },
                 'director_field': {
                     'isOfType': ['builder']
                 },
                 'construct': {
                     'invokes': ['build_step', 'get_result']
                 },
                 'builder': {
                     'has': ['build_step', 'get_result']
                 },
                 'get_result': {
                     'hasReturnType': ['product']
                 },
                 'product': {
                     'has': ['product_method']
                 },
                 'concrete_builder': {
                     'implements': ['builder'],
                     'has': ['product_field', 'concrete_step',
                             'concrete_get_result']
                 },
                 'product_field': {
                     'isOfType': ['product'],
                     'instantiates': ['product']
                 },
                 'concrete_step': {
                     'overrides': ['build_step'],
                     'invokes': ['product_method']
                 },
                 'concrete_get_result': {
                     'overrides': ['get_result'],
                     'returns': ['product_field']
                 }
             }),
        'prototype':
            ({
                 'prototype': Interface(),
                 'copy': AbstractMethod(),
                 'concrete_prototype': Class(),
                 'concrete_copy': Method(),
                 'client': Method()
             },
             {
                 'prototype': {
                     'has': ['copy']
                 },
                 'copy': {
                     'hasReturnType': ['prototype']
                 },
                 'concrete_prototype': {
                     'implements': ['prototype'],
                     'has': ['concrete_copy']
                 },
                 'concrete_copy': {
                     'overrides': ['copy'],
                     'instantiates': ['concrete_prototype']
                 },
                 'client': {
                     'invokes': ['copy']
                 }
             }),

        # Structural patterns
        'adapter':
            ({
                 'target': Interface(),
                 'target_method': AbstractMethod(),
                 'adapter': Class(),
                 'adapter_method': Method(),
                 'adaptee_field': Field(),
                 'adaptee': Class(),
                 'adaptee_method': Method()
             },
             {
                 'target': {
                     'has': ['target_method']
                 },
                 'adapter': {
                     'implements': ['target'],
                     'has': ['adaptee_field', 'adapter_method']
                 },
                 'adaptee_field': {
                     'isOfType': ['adaptee']
                 },
                 'adapter_method': {
                     'overrides': ['target_method'],
                     'invokes': ['adaptee_method']
                 },
                 'adaptee': {
                     'has': ['adaptee_method']
                 }
             }),
        'bridge':
            ({
                 'abstraction': AbstractClass(),
                 'implementor_field': Field(),
                 'abstract_operation': AbstractMethod(),
                 'implementor': Interface(),
                 'implementor_method': AbstractMethod(),
                 'refined_abstraction': Class(),
                 'refined_operation': Method(),
                 'concrete_implementor': Class()
             },
             {
                 'abstraction': {
                     'has': ['implementor_field', 'abstract_operation']
                 },
                 'implementor_field': {
                     'isOfType': ['implementor']
                 },
                 'implementor': {
                     'has': ['implementor_method']
                 },
                 'refined_abstraction': {
                     'extends': ['abstraction'],
                     'has': ['refined_operation']
                 },
                 'refined_operation': {
                     'overrides': ['abstract_operation'],
                     'invokes': ['implementor_method']
                 },
                 'concrete_implementor': {
                     'implements': ['implementor']
                 }
             }),
        'composite':
            ({
                 'component': Interface(),
                 'operation': AbstractMethod(),
                 'leaf': Class(),
                 'composite': Class(),
                 'children': Field(),
                 'add': Method(),
                 'composite_operation': Method()
             },
             {
                 'component': {
                     'has': ['operation']
                 },
                 'leaf': {
                     'implements': ['component']
                 },
                 'composite': {
                     'implements': ['component'],
                     'has': ['children', 'add', 'composite_operation']
                 },
                 'children': {
                     'isCollectionOf': ['component']
                 },
                 'add': {
                     'parameterOfType': ['component']
                 },
                 'composite_operation': {
                     'overrides': ['operation'],
                     'invokes': ['operation']
                 }
             }),
        'decorator':
            ({
                 'component': Interface(),
                 'operation': AbstractMethod(),
                 'concrete_component': Class(),
                 'decorator': AbstractClass(),
                 'wrapped': Field(),
                 'concrete_decorator': Class(),
                 'decorated_operation': Method()
             },
             {
                 'component': {
                     'has': ['operation']
                 },
                 'concrete_component': {
                     'implements': ['component']
                 },
                 'decorator': {
                     'implements': ['component'],
                     'has': ['wrapped']
                 },
                 'wrapped': {
                     'isOfType': ['component']
                 },
                 'concrete_decorator': {
                     'extends': ['decorator'],
                     'has': ['decorated_operation']
                 },
                 'decorated_operation': {
                     'overrides': ['operation'],
                     'invokes': ['operation']
                 }
             }),
        'facade':
            ({
                 'facade': Class(),
                 'facade_method': Method(),
                 'subsystem_field_a': Field(),
                 'subsystem_field_b': Field(),
                 'subsystem_a': Class(),
                 'subsystem_b': Class(),
                 'subsystem_method_a': Method(),
                 'subsystem_method_b': Method()
             },
             {
                 'facade': {
                     'has': ['subsystem_field_a', 'subsystem_field_b',
                             'facade_method']
                 },
                 'facade_method': {
                     'invokes': ['subsystem_method_a', 'subsystem_method_b']
                 },
                 'subsystem_field_a': {
                     'isOfType': ['subsystem_a']
                 },
                 'subsystem_field_b': {
                     'isOfType': ['subsystem_b']
                 },
                 'subsystem_a': {
                     'has': ['subsystem_method_a']
                 },
                 'subsystem_b': {
                     'has': ['subsystem_method_b']
                 }
             }),
        'flyweight':
            ({
                 'flyweight': Interface(),
                 'operation': AbstractMethod(),
                 'concrete_flyweight': Class(),
                 'intrinsic_state': Field(),
                 'flyweight_factory': Class(),
                 'pool': Field(),
                 'get_flyweight': Method()
             },
             {
                 'flyweight': {
                     'has': ['operation']
                 },
                 'concrete_flyweight': {
                     'implements': ['flyweight'],
                     'has': ['intrinsic_state']
                 },
                 'flyweight_factory': {
                     'has': ['pool', 'get_flyweight']
                 },
                 'pool': {
                     'isCollectionOf': ['flyweight']
                 },
                 'get_flyweight': {
                     'hasReturnType': ['flyweight'],
                     'instantiates': ['concrete_flyweight']
                 }
             }),
        'proxy':
            ({
                 'subject': Interface(),
                 'subject_method': AbstractMethod(),
                 'real_subject': Class(),
                 'real_method': Method(),
                 'proxy': Class(),
                 'real_field': Field(),
                 'proxy_method': Method()
             },
             {
                 'subject': {
                     'has': ['subject_method']
                 },
                 'real_subject': {
                     'implements': ['subject'],
                     'has': ['real_method']
                 },
                 'real_method': {
                     'overrides': ['subject_method']
                 },
                 'proxy': {
                     'implements': ['subject'],
                     'has': ['real_field', 'proxy_method']
                 },
                 'real_field': {
                     'isOfType': ['real_subject']
                 },
                 'proxy_method': {
                     'overrides': ['subject_method'],
                     'invokes': ['real_method']
                 }
             }),

        # Behavioural patterns
        'chainOfResponsibility':
            ({
                 'handler': AbstractClass(),
                 'next_handler': Field(),
                 'handle': Method(),
                 'abstract_step': AbstractMethod(),
                 'concrete_handler': Class(),
                 'concrete_step': Method()
             },
             {
                 'handler': {
                     'has': ['next_handler', 'handle', 'abstract_step']
                 },
                 'next_handler': {
                     'isOfType': ['handler']
                 },
                 # The request is passed along the chain by handle invoking
                 # itself on the next handler
                 'handle': {
                     'invokes': ['handle', 'abstract_step']
                 },
                 'concrete_handler': {
                     'extends': ['handler'],
                     'has': ['concrete_step']
                 },
                 'concrete_step': {
                     'overrides': ['abstract_step']
                 }
             }),
        'command':
            ({
                 'command': Interface(),
                 'execute': AbstractMethod(),
                 'concrete_command': Class(),
                 'receiver_field': Field(),
                 'receiver': Class(),
                 'receiver_method': Method(),
                 'concrete_execute': Method(),
                 'invoker': Class(),
                 'add_command': Method(),
                 'invoke': Method()
             },
             {
                 'command': {
                     'has': ['execute']
                 },
                 'concrete_command': {
                     'implements': ['command'],
                     'has': ['receiver_field', 'concrete_execute']
                 },
                 'receiver_field': {
                     'isOfType': ['receiver']
                 },
                 'receiver': {
                     'has': ['receiver_method']
                 },
                 'concrete_execute': {
                     'overrides': ['execute'],
                     'invokes': ['receiver_method']
                 },
                 'invoker': {
                     'has': ['add_command', 'invoke']
                 },
                 'add_command': {
                     'parameterOfType': ['command']
                 },
                 'invoke': {
                     'invokes': ['execute']
                 }
             }),
        'interpreter':
            ({
                 'expression': Interface(),
                 'interpret': AbstractMethod(),
                 'context': Class(),
                 'terminal': Class(),
                 'nonterminal': Class(),
                 'child_field': Field(),
                 'nonterminal_interpret': Method()
             },
             {
                 'expression': {
                     'has': ['interpret']
                 },
                 'interpret': {
                     'parameterOfType': ['context']
                 },
                 'terminal': {
                     'implements': ['expression']
                 },
                 'nonterminal': {
                     'implements': ['expression'],
                     'has': ['child_field', 'nonterminal_interpret']
                 },
                 'child_field': {
                     'isOfType': ['expression']
                 },
                 'nonterminal_interpret': {
                     'overrides': ['interpret'],
                     'invokes': ['interpret']
                 }
             }),
        'iterator':
            ({
                 'iterator': Interface(),
                 'has_next': AbstractMethod(),
                 'next_item': AbstractMethod(),
                 'aggregate': Interface(),
                 'create_iterator': AbstractMethod(),
                 'concrete_iterator': Class(),
                 'concrete_aggregate': Class(),
                 'concrete_create_iterator': Method()
             },
             {
                 'iterator': {
                     'has': ['has_next', 'next_item']
                 },
                 'aggregate': {
                     'has': ['create_iterator']
                 },
                 'create_iterator': {
                     'hasReturnType': ['iterator']
                 },
                 'concrete_iterator': {
                     'implements': ['iterator']
                 },
                 'concrete_aggregate': {
                     'implements': ['aggregate'],
                     'has': ['concrete_create_iterator']
                 },
                 'concrete_create_iterator': {
                     'overrides': ['create_iterator'],
                     'instantiates': ['concrete_iterator']
                 }
             }),
        'mediator':
            ({
                 'mediator': Interface(),
                 'relay': AbstractMethod(),
                 'colleague': AbstractClass(),
                 'mediator_field': Field(),
                 'send': Method(),
                 'receive': AbstractMethod(),
                 'concrete_mediator': Class(),
                 'concrete_relay': Method(),
                 'concrete_colleague': Class()
             },
             {
                 'mediator': {
                     'has': ['relay']
                 },
                 'relay': {
                     'parameterOfType': ['colleague']
                 },
                 'colleague': {
                     'has': ['mediator_field', 'send', 'receive']
                 },
                 'mediator_field': {
                     'isOfType': ['mediator']
                 },
                 'send': {
                     'invokes': ['relay']
                 },
                 'concrete_mediator': {
                     'implements': ['mediator'],
                     'has': ['concrete_relay']
                 },
                 'concrete_relay': {
                     'overrides': ['relay'],
                     'invokes': ['receive']
                 },
                 'concrete_colleague': {
                     'extends': ['colleague']
                 }
             }),
        'memento':
            ({
                 'originator': Class(),
                 'originator_state': Field(),
                 'save': Method(),
                 'restore': Method(),
                 'memento': Class(),
                 'state': Field(),
                 'get_state': Method(),
                 'caretaker': Class(),
                 'store': Method(),
                 'retrieve': Method()
             },
             {
                 'originator': {
                     'has': ['originator_state', 'save', 'restore']
                 },
                 'save': {
                     'hasReturnType': ['memento'],
                     'instantiates': ['memento']
                 },
                 'restore': {
                     'parameterOfType': ['memento'],
                     'invokes': ['get_state'],
                     'assigns': ['originator_state']
                 },
                 'memento': {
                     'has': ['state', 'get_state']
                 },
                 'get_state': {
                     'returns': ['state']
                 },
                 'caretaker': {
                     'has': ['store', 'retrieve']
                 },
                 'store': {
                     'parameterOfType': ['memento']
                 },
                 'retrieve': {
                     'hasReturnType': ['memento']
                 }
             }),
        'observer':
            ({
                 'subject': Class(),
                 'observers': Field(),
                 'attach': Method(),
                 'notify': Method(),
                 'observer': Interface(),
                 'update': AbstractMethod(),
                 'concrete_observer': Class()
             },
             {
                 'subject': {
                     'has': ['observers', 'attach', 'notify']
                 },
                 'observers': {
                     'isCollectionOf': ['observer']
                 },
                 'attach': {
                     'parameterOfType': ['observer']
                 },
                 'notify': {
                     'invokes': ['update']
                 },
                 'observer': {
                     'has': ['update']
                 },
                 'concrete_observer': {
                     'implements': ['observer']
                 }
             }),
        'state':
            ({
                 'context': Class(),
                 'state_field': Field(),
                 'set_state': Method(),
                 'request': Method(),
                 'state': Interface(),
                 'handle': AbstractMethod(),
                 'concrete_state': Class(),
                 'transition': Method(),
                 'next_state': Class()
             },
             {
                 'context': {
                     'has': ['state_field', 'set_state', 'request']
                 },
                 'state_field': {
                     'isOfType': ['state']
                 },
                 'set_state': {
                     'parameterOfType': ['state'],
                     'assigns': ['state_field']
                 },
                 'request': {
                     'invokes': ['handle']
                 },
                 'state': {
                     'has': ['handle']
                 },
                 'handle': {
                     'parameterOfType': ['context']
                 },
                 'concrete_state': {
                     'implements': ['state']
                 },
                 'transition': {
                     'instantiates': ['next_state']
                 },
                 'next_state': {
                     'implements': ['state']
                 }
             }),
        'visitor':
            ({
                 'element': Interface(),
                 'accept': AbstractMethod(),
                 'visitor': Interface(),
                 'visit_a': AbstractMethod(),
                 'visit_b': AbstractMethod(),
                 'concrete_element_a': Class(),
                 'concrete_element_b': Class(),
                 'accept_a': Method(),
                 'accept_b': Method(),
                 'concrete_visitor': Class()
             },
             {
                 'element': {
                     'has': ['accept']
                 },
                 'accept': {
                     'parameterOfType': ['visitor']
                 },
                 'visitor': {
                     'has': ['visit_a', 'visit_b']
                 },
                 'visit_a': {
                     'parameterOfType': ['concrete_element_a']
                 },
                 'visit_b': {
                     'parameterOfType': ['concrete_element_b']
                 },
                 'concrete_element_a': {
                     'implements': ['element'],
                     'has': ['accept_a']
                 },
                 'concrete_element_b': {
                     'implements': ['element'],
                     'has': ['accept_b']
                 },
                 'accept_a': {
                     'overrides': ['accept'],
                     'invokes': ['visit_a']
                 },
                 'accept_b': {
                     'overrides': ['accept'],
                     'invokes': ['visit_b']
                 },
                 'concrete_visitor': {
                     'implements': ['visitor']
                 }
             })}

    # The patterns above are general, and are used for every language. A
    # pattern is only redefined for a language here when the general
    # definition cannot apply to it.
    language_overrides = {
        # Python has no private constructors and its types are optional, so
        # a Singleton is a class holding a private class attribute that is
        # reached through a static method, a class method or __new__
        ('singleton', 'python'):
            ({
                 'singleton': Class(),
                 'private instance': Field(
                     info={'modifiers': {'private', 'static'}}),
                 'get_instance': Method(info={'modifiers': {'static'}})
             },
             {
                 'singleton': {
                     'has': ['private instance', 'get_instance']
                 },
                 'private instance': {
                     'instantiates': ['singleton']
                 },
                 'get_instance': {
                     'returns': ['private instance']
                 }
             })}

    if (pattern, language) in language_overrides:
        return language_overrides[(pattern, language)]
    if pattern in pattern_dict.keys():
        return pattern_dict[pattern]
    return None, None


# The relation that each relation is recorded as on the entity it leads to
INVERSES = {'has': 'composes', 'extends': 'extendedBy',
            'implements': 'implementedBy', 'instantiates': 'instantiatedBy',
            'overrides': 'overridenBy', 'invokes': 'invokedBy',
            'parameterOfType': 'typeOfParameter', 'isOfType': 'isTypeOf',
            'isCollectionOf': 'isElementTypeOf',
            'hasReturnType': 'isReturnTypeOf', 'assigns': 'assignedBy',
            'returns': 'returnedBy'}


class Match:
    """An instance of a pattern: the entities found for each of its roles.
    An instance that is almost complete has nothing for the roles in
    missing."""

    def __init__(self, pattern, roles, missing=()):
        self.pattern = pattern
        self.roles = roles
        self.missing = list(missing)

    def __str__(self):
        text = f'Found potential instance of {self.pattern} pattern:\n'
        for role, entities in self.roles.items():
            text += f' -{role.upper()}:\n'
            for entity in entities:
                text += f'{entity}\n'
        return text


class RoleSearch:
    """Searches a graph for ways to give a different entity to each role of
    a pattern, so that every relation between two roles holds between the
    entities given to them. The first role is the anchor: each entity that
    can fill it is the start of a separate instance of the pattern."""

    def __init__(self, entity_dict, relation_dict, roles, entities_by_type,
                 expected=None):
        self.roles = roles
        self.anchor = roles[0]
        self.entity_dict = entity_dict
        self.entities_by_type = entities_by_type
        # For some roles, relations that an entity filling the role must
        # have with any entity of a given type
        self.expected = expected or {}
        self.edges = [(source, relation, target)
                      for source, relations in relation_dict.items()
                      for relation, targets in relations.items()
                      for target in targets
                      if source in roles and target in roles]
        # For each role, its relations with the other roles: the relation,
        # the other role, and whether the relation leads to that role
        self.links = {role: [] for role in roles}
        for source, relation, target in self.edges:
            if source != target:
                self.links[source].append((relation, target, True))
                self.links[target].append((relation, source, False))
        self.pools = {}

    def fits(self, role, entity):
        pattern_entity = self.entity_dict[role]
        return (not_none_check(pattern_entity.type, entity.type)
                and check_dict(pattern_entity.info, entity.info)
                # A role related to itself, such as a method that invokes
                # itself, needs an entity that is related to itself
                and all(entity in entity.relations[relation]
                        for source, relation, target in self.edges
                        if source == target == role)
                and all(any(related.type == entity_type
                            for related in entity.relations[relation])
                        for relation, entity_type in self.expected.get(
                            role, ())))

    def pool(self, role):
        """Returns every entity in the graph that could fill a role."""
        if role not in self.pools:
            self.pools[role] = [
                entity for entity in self.entities_by_type.get(
                    self.entity_dict[role].type, ())
                if self.fits(role, entity)]
        return self.pools[role]

    def order(self):
        """Returns the roles in an order where each is related to one before
        it wherever possible, beginning with the anchor."""
        ordered = [self.anchor]
        remaining = self.roles[1:]
        while remaining:
            related = [role for role in remaining
                       if any(other in ordered
                              for _, other, _ in self.links[role])]
            # A role related to none of the others can come at any point
            following = related[0] if related else remaining[0]
            ordered.append(following)
            remaining = [role for role in remaining if role != following]
        return ordered

    def reachable(self, role, domains):
        """Returns the entities that could fill a role, going by those that
        could fill the roles it is related to that already have a domain."""
        found = None
        for relation, other, outgoing in self.links[role]:
            if other not in domains:
                continue
            # The role's entities are found from those of the other role
            inverse = INVERSES[relation] if outgoing else relation
            related = {id(entity): entity
                       for other_entity in domains[other].values()
                       for entity in other_entity.relations[inverse]}
            found = related if found is None else {
                key: entity for key, entity in found.items()
                if key in related}
        if found is None:
            found = {id(entity): entity for entity in self.pool(role)}
        return {key: entity for key, entity in found.items()
                if self.fits(role, entity)}

    def narrow(self, anchor_entity):
        """Returns the entities that could fill each role alongside the
        anchor, having left out any that are not related as the role needs
        to an entity that could fill each related role. Returns None if
        that leaves a role with nothing to fill it."""
        domains = {self.anchor: {id(anchor_entity): anchor_entity}}
        for role in self.order()[1:]:
            domains[role] = self.reachable(role, domains)
            if not domains[role]:
                return None

        changed = True
        while changed:
            changed = False
            for source, relation, target in self.edges:
                if source == target:
                    continue
                targets = domains[target]
                sources = {
                    key: entity for key, entity in domains[source].items()
                    if any(id(other) in targets
                           for other in entity.relations[relation])}
                reached = {id(other) for entity in sources.values()
                           for other in entity.relations[relation]}
                targets = {key: entity for key, entity in targets.items()
                           if key in reached}
                if not sources or not targets:
                    return None
                if (len(sources) < len(domains[source])
                        or len(targets) < len(domains[target])):
                    domains[source], domains[target] = sources, targets
                    changed = True
        return domains

    def consistent(self, role, entity, binding):
        """Checks that an entity could fill a role alongside the entities
        already bound to other roles."""
        for relation, other, outgoing in self.links[role]:
            if other not in binding:
                continue
            source, target = ((entity, binding[other]) if outgoing
                              else (binding[other], entity))
            if target not in source.relations[relation]:
                return False
        return all(entity is not bound for bound in binding.values())

    def solve(self, domains, fixed):
        """Returns a different entity for every role, including those given
        for the fixed roles, or None if there is no such assignment."""
        binding = {}
        for role, entity in fixed.items():
            if not self.consistent(role, entity, binding):
                return None
            binding[role] = entity

        def extend():
            unbound = [role for role in self.roles if role not in binding]
            if not unbound:
                return True
            # The role with fewest entities to try is bound next, taking
            # those related to a bound role first
            role = min(unbound, key=lambda unbound_role: (
                not any(other in binding
                        for _, other, _ in self.links[unbound_role]),
                len(domains[unbound_role])))
            for entity in domains[role].values():
                if self.consistent(role, entity, binding):
                    binding[role] = entity
                    if extend():
                        return True
                    del binding[role]
            return False

        return dict(binding) if extend() else None

    def instance(self, anchor_entity):
        """Returns the entities that can fill each role alongside the one
        given for the anchor, or None if the roles cannot all be filled."""
        domains = self.narrow(anchor_entity)
        if domains is None:
            return None
        solution = self.solve(domains, {self.anchor: anchor_entity})
        if solution is None:
            return None

        # An entity is kept for a role only if it is part of an assignment
        # of an entity to every role
        supported = {role: {id(entity)} for role, entity in solution.items()}
        for role in self.roles[1:]:
            for key, candidate in domains[role].items():
                if key in supported[role]:
                    continue
                solution = self.solve(domains, {self.anchor: anchor_entity,
                                                role: candidate})
                for other, entity in (solution or {}).items():
                    supported[other].add(id(entity))

        return {role: [entity for key, entity in domains[role].items()
                       if key in supported[role]]
                for role in self.roles}

    def instances(self):
        found = (self.instance(entity) for entity in self.pool(self.anchor))
        return [instance for instance in found if instance is not None]


class DesignPattern:
    def __init__(self, pattern='singleton'):
        self.pattern = pattern
        self.entity_dict, self.relation_dict = pattern_library(pattern)

        if self.entity_dict is None:
            raise ValueError(f'Unknown design pattern: {pattern}')

    def connected_roles(self, without):
        """Returns the roles still related to the first role, directly or
        through other roles, when one role is left out."""
        roles = [role for role in self.entity_dict if role != without]
        connected = roles[:1]
        for role in connected:
            for source, relations in self.relation_dict.items():
                for targets in relations.values():
                    for target in targets:
                        for near, far in ((source, target), (target, source)):
                            if (near == role and far in roles
                                    and far not in connected):
                                connected.append(far)
        return [role for role in roles if role in connected]

    def find_matches(self, graph, language=None):
        """Returns the instances of the pattern in a graph. If there are
        none, returns those that are complete but for one role, and any
        roles that are only related to the rest of the pattern through
        it. A role related to the missing one must still be related in that
        way to an entity of the right type, so that an instance is almost
        complete when what should fill the role is there but falls short.
        """
        self.entity_dict, self.relation_dict = pattern_library(self.pattern,
                                                               language)
        entities_by_type = {}
        for entity in graph['entities']:
            entities_by_type.setdefault(entity.type, []).append(entity)

        def search(roles, expected=None):
            return RoleSearch(self.entity_dict, self.relation_dict, roles,
                              entities_by_type, expected).instances()

        roles = list(self.entity_dict)
        complete = search(roles)
        if complete:
            return [Match(self.pattern, instance) for instance in complete]

        # The role whose absence leaves most of the pattern is reported
        missing, almost = [], []
        for role in roles[1:]:
            kept = self.connected_roles(without=role)
            # An instance missing most of its roles is not almost complete
            if len(kept) * 2 < len(roles) or (
                    almost and len(roles) - len(kept) >= len(missing)):
                continue
            expected = {}
            for source, relations in self.relation_dict.items():
                for relation, targets in relations.items():
                    if role in targets and source in kept:
                        expected.setdefault(source, []).append(
                            (relation, self.entity_dict[role].type))
            instances = search(kept, expected)
            if instances:
                almost = instances
                missing = [role] + [other for other in roles
                                    if other not in kept and other != role]
        return [Match(self.pattern, instance, missing)
                for instance in almost]

    def describe(self, matches):
        """Returns the feedback to give for the matches found."""
        if not matches:
            return (f'Could not find any potential instances of '
                    f'{self.pattern} pattern')
        if matches[0].missing:
            return (f'Implementation of {self.pattern} pattern is almost '
                    f'complete: \n MISSING ENTITY: {matches[0].missing[0]}')
        return ''.join(str(match) for match in matches)
