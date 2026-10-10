import ast
import os.path

from src.entity_relations.er_classes import (
    AbstractClass, AbstractMethod, Class, Constructor, Extends, Field, Has,
    HasReturnType, Implements, Instantiates, Interface, Invokes, IsOfType,
    Method, Overrides, ParameterOfType)
from src.entity_relations.graph_display import print_graph
from src.entity_relations.utils import add_node_to_dict, find_in_dict
from src.filters.python_filter import (
    FUNCTIONS, PythonFilter, base_names, classify, identifier,
    is_abstract_class, is_abstract_method)

CLASS_TYPES = ('class', 'abstractClass', 'interface')


def first_pass(file, first_pass_dict):
    package_name = file.relative_path
    full_file_name = os.path.join(file.relative_path, file.file_name)

    file_entities = []
    file_relations = []
    class_entities = {}

    for kind, node, owner in classify(file.ast):
        name = PythonFilter.name_of(node)
        location = {'node': node, 'package': package_name,
                    'file': full_file_name}

        if kind in ('class', 'interface'):
            if kind == 'interface':
                entity_type = Interface
            else:
                entity_type = (AbstractClass if is_abstract_class(node)
                               else Class)
            entity = entity_type(info={'name': name}, **location)
            class_entities[id(node)] = entity
            file_entities.append(entity)
            add_node_to_dict(first_pass_dict, name, entity)
            continue

        owner_entity = class_entities.get(id(owner))
        if owner_entity is None:
            continue

        info = {'modifiers': PythonFilter.modifiers_of(node), 'name': name}
        if kind == 'method':
            # As in Java, every method of an interface is abstract
            abstract = (owner_entity.type == 'interface'
                        or is_abstract_method(node))
            entity_type = AbstractMethod if abstract else Method
        elif kind == 'constructor':
            info['name'] = f'{owner.name} Constructor'
            entity_type = Constructor
        elif kind == 'field':
            info['type'] = (identifier(node.annotation)
                            if isinstance(node, ast.AnnAssign) else None)
            entity_type = Field
        else:
            continue

        entity = entity_type(info=info, **location)
        file_entities.append(entity)
        add_node_to_dict(first_pass_dict, info['name'], entity)
        file_relations.append(Has(owner_entity, entity))

    return file_entities, file_relations


def parameters(function):
    arguments = function.args
    return arguments.posonlyargs + arguments.args + arguments.kwonlyargs


def enclosing_method(field_entity):
    """Returns the method in which a field is assigned, if any."""
    for owner in field_entity.relations['composes']:
        for member in owner.node.body:
            if isinstance(member, FUNCTIONS) and any(
                    node is field_entity.node for node in ast.walk(member)):
                return member
    return None


def field_type_name(field_entity):
    """Fields are rarely annotated in Python, so the type is otherwise taken
    from the value assigned: either the class instantiated, or the annotation
    of the parameter the field is set from."""
    node = field_entity.node
    if field_entity.info['type'] is not None:
        return field_entity.info['type']

    if isinstance(node.value, ast.Call):
        return identifier(node.value.func)

    if isinstance(node.value, ast.Name):
        method = enclosing_method(field_entity)
        if method is not None:
            for parameter in parameters(method):
                if parameter.arg == node.value.id:
                    return identifier(parameter.annotation)
    return None


def build_python_graph(files, display=False):
    entities = []
    relations = []
    first_pass_dict = {}

    def find_class(name, origin):
        if name is None:
            return None
        related_entity = find_in_dict(name, first_pass_dict, origin)
        if related_entity is None or related_entity.type not in CLASS_TYPES:
            return None
        return related_entity

    # Initial Pass
    for file in files:
        file_entities, file_relations = first_pass(file, first_pass_dict)
        entities.extend(file_entities)
        relations.extend(file_relations)

        if display:
            print_graph(file_entities, file_relations)

    for entity in entities:
        node = entity.node
        if entity.type in CLASS_TYPES:
            # Class - Extends, or Implements if the base is an interface
            for base in base_names(node):
                related_entity = find_class(base, entity)
                if related_entity is None:
                    continue
                if (related_entity.type == 'interface'
                        and entity.type != 'interface'):
                    relations.append(Implements(entity, related_entity))
                else:
                    relations.append(Extends(entity, related_entity))
        elif entity.type in ('abstractMethod', 'method', 'constructor'):
            # Parameter
            for parameter in parameters(node):
                related_entity = find_class(identifier(parameter.annotation),
                                            entity)
                if related_entity is not None:
                    relations.append(ParameterOfType(entity, related_entity))
            # ReturnType
            related_entity = find_class(identifier(node.returns), entity)
            if related_entity is not None:
                relations.append(HasReturnType(entity, related_entity))
            if entity.type == 'method':
                # Method - Overrides
                for owner in entity.relations['composes']:
                    for interface_entity in owner.relations['implements']:
                        for member in interface_entity.relations['has']:
                            if member.type == 'abstractMethod':
                                if member.info['name'] == entity.info['name']:
                                    relations.append(Overrides(entity, member))
                    for parent_entity in owner.relations['extends']:
                        for member in parent_entity.relations['has']:
                            if member.type in ['abstractMethod', 'method']:
                                if member.info['name'] == entity.info['name']:
                                    relations.append(Overrides(entity, member))
            if entity.type != 'abstractMethod':
                # Invokes, or Instantiates if a class is called
                for call in ast.walk(node):
                    if not isinstance(call, ast.Call):
                        continue
                    name = identifier(call.func)
                    if name is None:
                        continue
                    related_entity = find_in_dict(name, first_pass_dict,
                                                  entity)
                    if related_entity is None:
                        continue
                    if related_entity.type in CLASS_TYPES:
                        relations.append(Instantiates(entity, related_entity))
                    else:
                        relations.append(Invokes(entity, related_entity))
        elif entity.type == 'field':
            # Field - Type
            related_entity = find_class(field_type_name(entity), entity)
            if related_entity is not None:
                relations.append(IsOfType(entity, related_entity))

    if display:
        print_graph(entities, relations)

    return {'entities': entities, 'relations': relations}
