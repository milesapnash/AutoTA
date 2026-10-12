from src.graph.er_classes import Extends, Implements
from src.graph.symbols import CLASS_TYPES, find_entity, relation_adder


class SecondPass:
    """Adds the relations between the entities found by the first pass. A
    language says how what it imports is found, and which types a class is
    derived from."""

    def __init__(self, relations, first_pass_dict, imports):
        self.first_pass_dict = first_pass_dict
        self.imports = imports
        self.relate = relation_adder(relations)

    def is_imported(self, origin, entity):
        raise NotImplementedError

    def supertype_names(self, entity):
        raise NotImplementedError

    def find_type(self, name, origin):
        if name is None:
            return None
        return find_entity(name, self.first_pass_dict, origin,
                           types=CLASS_TYPES, imported=self.is_imported)

    # Class - Extends, or Implements if the supertype is an interface
    def add_supertypes(self, entity):
        if entity.type not in CLASS_TYPES:
            return
        for supertype in self.supertype_names(entity):
            related_entity = self.find_type(supertype, entity)
            if related_entity is None:
                continue
            if (related_entity.type == 'interface'
                    and entity.type != 'interface'):
                self.relate(Implements, entity, related_entity)
            else:
                self.relate(Extends, entity, related_entity)
