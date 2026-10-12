from collections import namedtuple

from src.graph.er_classes import Overrides

CLASS_TYPES = ('class', 'abstractClass', 'interface')
METHOD_TYPES = ('method', 'abstractMethod')

# The type of an expression: the class it is an instance of, and the class it
# is a collection of. Either is None when it is not a class in the project,
# and an expression whose type could not be worked out has no Typed at all.
Typed = namedtuple('Typed', ['type', 'element'])
EXTERNAL = Typed(None, None)


def add_node_to_dict(node_dict, key, item):
    if key in node_dict:
        node_dict[key].append(item)
    else:
        node_dict[key] = [item]


def find_in_dict(name, name_dict, origin, types=None, imported=None):
    """Finds the entity that a name refers to from origin. If several
    entities share the name, one in the same file is preferred, then one
    that the file imports, then one in the same package."""
    candidates = [entity for entity in name_dict.get(name, ())
                  if types is None or entity.type in types]
    if len(candidates) == 1:
        return candidates[0]

    file_visible = [entity for entity in candidates
                    if entity.package == origin.package
                    and entity.file == origin.file]
    if len(file_visible) > 0:
        return file_visible[0]

    import_visible = [entity for entity in candidates
                      if imported is not None and imported(origin, entity)]
    if len(import_visible) == 1:
        return import_visible[0]

    package_visible = [entity for entity in candidates
                       if entity.package == origin.package]
    if len(package_visible) == 1:
        return package_visible[0]
    return None


def find_unique(name, name_dict, types):
    """Finds the entity with a name, if it is the only one of its kind."""
    candidates = [entity for entity in name_dict.get(name, ())
                  if entity.type in types]
    return candidates[0] if len(candidates) == 1 else None


def relation_adder(relations):
    """Returns a function that adds a relation between two entities, unless
    they are already related in that way."""
    seen = set()

    def relate(relation_type, source, target):
        key = (relation_type, id(source), id(target))
        if key not in seen:
            seen.add(key)
            relations.append(relation_type(source, target))

    return relate


def supertypes(class_entity):
    """Returns every class and interface that a class inherits from, with
    the nearest first."""
    found = []
    queue = [class_entity]
    while queue:
        relations = queue.pop(0).relations
        for parent in relations['extends'] + relations['implements']:
            if parent is not class_entity and parent not in found:
                found.append(parent)
                queue.append(parent)
    return found


def enclosing_classes(class_entity):
    """Returns the classes that a class is declared within, with the nearest
    first."""
    found = []
    current = class_entity
    while current.relations['composes']:
        current = current.relations['composes'][0]
        if current is class_entity or current in found:
            break
        found.append(current)
    return found


def find_members(class_entity, name, types):
    """Returns the members with a name that a class declares or, if it
    declares none, those that it inherits."""
    for owner in [class_entity] + supertypes(class_entity):
        found = [member for member in owner.relations['has']
                 if member.type in types and member.info['name'] == name]
        if found:
            return found
    return []


def find_field(class_entity, name):
    found = find_members(class_entity, name, ('field',))
    return found[0] if found else None


def field_type(field):
    types = field.relations['isOfType']
    elements = field.relations['isCollectionOf']
    return Typed(types[0] if types else None,
                 elements[0] if elements else None)


def add_overrides(method, relate, overridable):
    """Relates a method to each method it overrides, in any of the classes
    and interfaces that its class inherits from."""
    for owner in method.relations['composes']:
        for parent in supertypes(owner):
            for member in parent.relations['has']:
                if (member.type in METHOD_TYPES
                        and member.info['name'] == method.info['name']
                        and overridable(method, member)):
                    relate(Overrides, method, member)
