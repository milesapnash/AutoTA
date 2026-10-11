from src.entity_relations.er_classes import (
    AbstractClass, AbstractMethod, Class, Constructor, Entity, Field,
    Interface, Method)


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


class DesignPattern:
    def __init__(self, pattern='singleton'):
        self.pattern = pattern
        self.entity_dict, self.relation_dict = pattern_library(pattern)

        if self.entity_dict is None:
            raise ValueError(f'Unknown design pattern: {pattern}')

    def relations_contained(self, pattern_relations, graph_relations):
        if pattern_relations is None:
            return True
        for relation_type in pattern_relations.keys():
            if len(pattern_relations[relation_type]) > len(
                    graph_relations[relation_type]):
                return False

            matching_types = [graph_relation.type for graph_relation in
                              graph_relations[relation_type]]

            for relation in pattern_relations[relation_type]:
                if self.entity_dict[relation].type not in matching_types:
                    return False

        return True

    def entity_expressed(self, pattern_entity, graph_entity, relations):
        return not_none_check(pattern_entity.type,
                              graph_entity.type) and check_dict(
            pattern_entity.info,
            graph_entity.info) and self.relations_contained(
            relations, graph_entity.relations)

    def find_potential_isomorphisms(self, graph, language=None):
        self.entity_dict, self.relation_dict = pattern_library(self.pattern,
                                                               language)
        node_dict = {}
        missing_nodes = []
        not_found = (f'Could not find any potential instances of '
                     f'{self.pattern} pattern')

        # Find all potential nodes for each entity
        for from_node_name, entity in self.entity_dict.items():
            relations = self.relation_dict.get(from_node_name)
            potential_isomorphisms = [graph_entity for graph_entity in
                                      graph['entities'] if
                                      self.entity_expressed(entity,
                                                            graph_entity,
                                                            relations)]
            if len(potential_isomorphisms) == 0:
                missing_nodes.append(from_node_name)
            else:
                node_dict[from_node_name] = potential_isomorphisms

        single_missing_node = None
        if len(missing_nodes) > 1:
            return not_found
        elif len(missing_nodes) == 1:
            single_missing_node = missing_nodes[0]
            node_dict[missing_nodes[0]] = [Entity()]

        for from_node_name, relations in self.relation_dict.items():
            for rel_type, to_node_names in relations.items():
                for to_node_name in to_node_names:
                    from_ents_to_remove = []
                    to_ents_to_remove = []

                    matching_from_entities = node_dict[from_node_name]
                    matching_to_entities = node_dict[to_node_name]
                    ents_to_matches = [False] * len(matching_to_entities)
                    if single_missing_node in (to_node_name, from_node_name):
                        continue

                    for matching_from_entity in matching_from_entities:
                        matched_from = False

                        for i, matching_to_entity in enumerate(
                                matching_to_entities):
                            if matching_to_entity in \
                                    matching_from_entity.relations[
                                        rel_type]:
                                matched_from = True
                                ents_to_matches[i] = True
                        if not matched_from:
                            from_ents_to_remove.append(matching_from_entity)

                    for i, matches in enumerate(ents_to_matches):
                        if not matches:
                            to_ents_to_remove.append(matching_to_entities[i])

                    for to_ent in to_ents_to_remove:
                        node_dict[to_node_name].remove(to_ent)
                        if not node_dict[to_node_name]:
                            if single_missing_node is not None:
                                return not_found
                            single_missing_node = to_node_name

                    for from_ent in from_ents_to_remove:
                        node_dict[from_node_name].remove(from_ent)
                        if not node_dict[from_node_name]:
                            if single_missing_node is not None:
                                return not_found
                            single_missing_node = from_node_name

        if single_missing_node is not None:
            return (f'Implementation of {self.pattern} pattern is almost '
                    f'complete: \n MISSING ENTITY: {single_missing_node}')

        return_string = (f'Found potential instance of {self.pattern} '
                         f'pattern:\n')
        for node_name, entities in node_dict.items():
            if len(entities) == 1:
                return_string += ' -' + node_name.upper() + ':\n' + str(
                    entities[0]) + '\n'
            else:
                return_string += ' -' + node_name.upper() + ':\n'
                for entity in entities:
                    return_string += str(entity) + '\n'

        return return_string
