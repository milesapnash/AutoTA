from src.entity_relations.pattern_library import pattern_library


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


def role_edges(relation_dict, roles):
    """Returns each relation between two of the roles, as the role it is
    from, the relation and the role it leads to."""
    return [(source, relation, target)
            for source, relations in relation_dict.items()
            for relation, targets in relations.items()
            for target in targets
            if source in roles and target in roles]


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
    entities given to them, and none of the forbidden relations does. The
    first role is the anchor: each entity that can fill it is the start of
    a separate instance of the pattern."""

    def __init__(self, entity_dict, relation_dict, forbidden_dict, roles,
                 entities_by_type, expected=None):
        self.roles = roles
        self.anchor = roles[0]
        self.entity_dict = entity_dict
        self.entities_by_type = entities_by_type
        # For some roles, relations that an entity filling the role must
        # have with any entity of a given type
        self.expected = expected or {}
        self.edges = role_edges(relation_dict, roles)
        # For each role, its relations with the other roles: the relation,
        # the other role, and whether the relation leads to that role
        self.links = self.links_of(self.edges)
        # The relations that each role must not have, in the same form
        self.forbidden_links = self.links_of(
            role_edges(forbidden_dict, roles))
        self.pools = {}

    def links_of(self, edges):
        links = {role: [] for role in self.roles}
        for source, relation, target in edges:
            if source != target:
                links[source].append((relation, target, True))
                links[target].append((relation, source, False))
        return links

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
        for links, required in ((self.links, True),
                                (self.forbidden_links, False)):
            for relation, other, outgoing in links[role]:
                if other not in binding:
                    continue
                source, target = ((entity, binding[other]) if outgoing
                                  else (binding[other], entity))
                if (target in source.relations[relation]) != required:
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
        definition = pattern_library(pattern)
        if definition is None:
            raise ValueError(f'Unknown design pattern: {pattern}')
        self.use(definition)

    def use(self, definition):
        self.entity_dict = definition.roles
        self.relation_dict = definition.relations
        self.forbidden_dict = definition.forbidden

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
        self.use(pattern_library(self.pattern, language))
        entities_by_type = {}
        for entity in graph['entities']:
            entities_by_type.setdefault(entity.type, []).append(entity)

        def search(roles, expected=None):
            return RoleSearch(self.entity_dict, self.relation_dict,
                              self.forbidden_dict, roles, entities_by_type,
                              expected).instances()

        roles = list(self.entity_dict)
        complete = search(roles)
        if complete:
            return [Match(self.pattern, instance) for instance in complete]

        # The role whose absence leaves most of the pattern is reported
        missing, almost = [], []
        restricted = {role for source, _, target in role_edges(
            self.forbidden_dict, roles) for role in (source, target)}
        for role in roles[1:]:
            kept = self.connected_roles(without=role)
            # An instance missing most of its roles is not almost complete
            if len(kept) * 2 < len(roles) or (
                    almost and len(roles) - len(kept) >= len(missing)):
                continue
            # Nor is one that has a relation it must not have, which leaving
            # out either of the roles it is between would hide
            if not restricted <= set(kept):
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
