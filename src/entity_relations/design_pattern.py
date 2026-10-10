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
                 'private instance': Field(
                     info={'modifiers': {'private'}}),
                 'get_instance': Method()
             }, {
                 'singleton': {
                     'has': ['private constructor',
                             'private instance',
                             'get_instance']
                 },
                 'private instance': {
                     'isOfType': ['singleton']
                 },
                 'get_instance': {
                     'hasReturnType': ['singleton']
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
                 'strategy': Interface(),
                 'strategy_method': AbstractMethod(),
                 'concrete_strategy': Class(),
                 'concrete_method': Method()
             },
             {
                 'context': {
                     'has': ['context_field']
                 },
                 'strategy': {
                     'has': ['strategy_method']
                 },
                 'concrete_strategy': {
                     'implements': ['strategy']
                 },
                 'context_field': {
                     'isOfType': ['strategy']
                 },
                 'concrete_method': {
                     'overrides': ['strategy_method']
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
                 'get_instance': Method(
                     info={'modifiers': {'static'}})
             }, {
                 'singleton': {
                     'has': ['private instance',
                             'get_instance']
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
