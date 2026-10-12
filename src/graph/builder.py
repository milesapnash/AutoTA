import os.path

from src.graph.er_classes import Extends, Has, Implements
from src.graph.graph_display import print_graph
from src.graph.symbols import CLASS_TYPES, find_entity, relation_adder


class FirstPass:
    """Creates the entities declared in a file, and the Has relations
    between each of them and the class it belongs to. A language finds the
    declarations in the file, and adds an entity for each."""

    def __init__(self, file, first_pass_dict, package):
        self.location = {
            'package': package,
            'file': os.path.join(file.relative_dir, file.file_name)}
        self.first_pass_dict = first_pass_dict
        self.entities = []
        self.relations = []

    def add(self, entity_type, name, node, owner=None, **attributes):
        entity = entity_type(name=name, node=node, **attributes,
                             **self.location)
        self.entities.append(entity)
        self.first_pass_dict.setdefault(name, []).append(entity)
        if owner is not None:
            self.relations.append(Has(owner, entity))
        return entity


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


def build_graph(files, first_pass, second_pass, display=False):
    """Builds the entity-relation graph of a project from the first and
    second pass of its language."""
    entities = []
    relations = []
    first_pass_dict = {}
    # The syntax tree of each file, by the file that its entities are in
    trees = {}

    for file in files:
        file_pass = first_pass(file, first_pass_dict)
        entities.extend(file_pass.entities)
        relations.extend(file_pass.relations)
        trees[file_pass.location['file']] = file.ast

        if display:
            print_graph(file_pass.entities, file_pass.relations)

    second_pass(entities, relations, first_pass_dict, trees)

    if display:
        print_graph(entities, relations)

    return {'entities': entities, 'relations': relations}
