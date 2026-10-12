import ast
import os.path

from src.graph.er_classes import (
    AbstractClass, AbstractMethod, Assigns, Class, Constructor, Field, Has,
    HasReturnType, Instantiates, Interface, Invokes, IsCollectionOf, IsOfType,
    Method, ParameterOfType, Returns)
from src.graph.graph_display import print_graph
from src.graph.second_pass import SecondPass
from src.graph.symbols import (
    CLASS_TYPES, EXTERNAL, METHOD_TYPES, Typed, add_overrides, field_type,
    find_field, find_members, find_unique)
from src.languages.python.filter import (
    FUNCTIONS, PythonFilter, base_names, class_kind, classify,
    decorator_names, identifier, is_abstract_class, is_abstract_method)

# Annotations that describe a single value rather than a collection of them
WRAPPERS = {'Optional', 'Union', 'Final', 'ClassVar', 'Annotated'}
LITERALS = (ast.List, ast.Dict, ast.Set, ast.Tuple, ast.JoinedStr,
            ast.ListComp, ast.DictComp, ast.SetComp)
COMPREHENSIONS = (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)


def first_pass(file, first_pass_dict):
    package_name = file.relative_dir
    full_file_name = os.path.join(file.relative_dir, file.file_name)

    file_entities = []
    file_relations = []
    class_entities = {}

    for kind, node, owner in classify(file.ast):
        name = PythonFilter.name_of(node)
        location = {'node': node, 'package': package_name,
                    'file': full_file_name}
        owner_entity = class_entities.get(id(owner))

        if kind in ('class', 'interface', 'enum'):
            if kind == 'interface':
                entity_type = Interface
            elif kind == 'enum':
                # An enum is a class whose members are fields of its own type
                entity_type = Class
            else:
                entity_type = (AbstractClass if is_abstract_class(node)
                               else Class)
            entity = entity_type(name=name, **location)
            class_entities[id(node)] = entity
            file_entities.append(entity)
            first_pass_dict.setdefault(name, []).append(entity)
            if owner_entity is not None:
                file_relations.append(Has(owner_entity, entity))
            continue

        if owner_entity is None:
            continue

        attributes = {'modifiers': PythonFilter.modifiers_of(node)}
        if kind == 'method':
            # As in Java, every method of an interface is abstract
            abstract = (owner_entity.type == 'interface'
                        or is_abstract_method(node))
            entity_type = AbstractMethod if abstract else Method
        elif kind == 'constructor':
            name = f'{owner.name} Constructor'
            entity_type = Constructor
        elif kind == 'field':
            attributes['declared_type'] = (
                identifier(node.annotation)
                if isinstance(node, ast.AnnAssign) else None)
            entity_type = Field
        else:
            continue

        entity = entity_type(name=name, **attributes, **location)
        file_entities.append(entity)
        first_pass_dict.setdefault(name, []).append(entity)
        file_relations.append(Has(owner_entity, entity))

    return file_entities, file_relations


def imports_of(tree):
    """Returns the modules that a file imports, each with the names that are
    imported from it, or None if the module itself is imported."""
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend((alias.name, None) for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported.append((node.module,
                             {alias.name for alias in node.names}))
    return imported


def imported_names(tree):
    """Returns the names that the imports of a file make available in it."""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.asname or alias.name.split('.')[0]
                         for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.update(alias.asname or alias.name for alias in node.names)
    return names


def parameters(function):
    arguments = function.args
    return arguments.posonlyargs + arguments.args + arguments.kwonlyargs


def enclosing_method(field_entity):
    """Returns the method in which a field is assigned, if any."""
    for owner in field_entity.relations['memberOf']:
        for member in owner.node.body:
            if isinstance(member, FUNCTIONS) and any(
                    node is field_entity.node for node in ast.walk(member)):
                return member
    return None


def annotation_names(annotation):
    """Returns the names that an annotation refers to: those of the type
    itself, and those of the types that it is a collection of."""
    if isinstance(annotation, ast.Constant):
        # An annotation may be written as a string
        if not isinstance(annotation.value, str):
            return [], []
        try:
            annotation = ast.parse(annotation.value, mode='eval').body
        except SyntaxError:
            return [], []

    if isinstance(annotation, (ast.Name, ast.Attribute)):
        return [identifier(annotation)], []
    if (isinstance(annotation, ast.BinOp)
            and isinstance(annotation.op, ast.BitOr)):
        left_named, left_elements = annotation_names(annotation.left)
        right_named, right_elements = annotation_names(annotation.right)
        return left_named + right_named, left_elements + right_elements
    if isinstance(annotation, ast.Subscript):
        arguments = annotation.slice
        arguments = (arguments.elts if isinstance(arguments, ast.Tuple)
                     else [arguments])
        named, elements = [], []
        for argument in arguments:
            argument_named, argument_elements = annotation_names(argument)
            named.extend(argument_named)
            elements.extend(argument_elements)
        if identifier(annotation.value) in WRAPPERS:
            return named, elements
        return [identifier(annotation.value)], named + elements
    return [], []


def is_super(node):
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == 'super')


class Scope:
    """The member that a piece of code belongs to, and the types of the
    parameters and local variables that the code can refer to."""

    def __init__(self, member, owner, variables=None, classes=None,
                 returns=True):
        self.member = member
        self.owner = owner
        self.variables = variables if variables is not None else {}
        # The names, such as cls, that refer to the class itself
        self.classes = classes if classes is not None else {}
        # Whether a return statement in the code returns from the member
        self.returns = returns

    def within_function(self):
        return Scope(self.member, self.owner, self.variables, self.classes,
                     returns=False)


class PythonSecondPass(SecondPass):
    def __init__(self, entities, relations, first_pass_dict, imports,
                 names):
        super().__init__(relations, first_pass_dict, imports)
        self.names = names
        # The class created by each call found to instantiate one
        self.instantiations = {}

        # Each step relies on the relations added by those before it
        for step in (self.add_supertypes, self.add_declared_types,
                     self.add_overridden, self.add_usages):
            for entity in entities:
                step(entity)

    def is_imported(self, origin, entity):
        module = os.path.splitext(entity.file)[0]
        module = module.replace('\\', '.').replace('/', '.')
        for imported, names in self.imports.get(origin.file, ()):
            if module == imported or module.endswith('.' + imported):
                if (names is None or '*' in names
                        or entity.name in names):
                    return True
        return False

    def supertype_names(self, entity):
        return base_names(entity.node)

    def referenced_types(self, annotation, origin):
        """Returns the classes that an annotation refers to: those that it
        names, and those that it is a collection of."""
        named, elements = annotation_names(annotation)
        return ([entity for entity in
                 (self.find_type(name, origin) for name in named)
                 if entity is not None],
                [entity for entity in
                 (self.find_type(name, origin) for name in elements)
                 if entity is not None])

    def typed(self, annotation, origin):
        """Returns the type that an annotation gives, which is not known
        when there is no annotation."""
        if annotation is None:
            return None
        named, elements = self.referenced_types(annotation, origin)
        return Typed(named[0] if named else None,
                     elements[0] if elements else None)

    def field_types(self, field):
        """Fields are rarely annotated in Python, so the type is otherwise
        taken from the value assigned: either the class instantiated, or the
        annotation of the parameter the field is set from."""
        node = field.node
        owner = field.relations['memberOf'][0]
        if isinstance(node, ast.AnnAssign):
            named, elements = self.referenced_types(node.annotation, field)
            if named or elements:
                return named, elements
        if (class_kind(owner.node) == 'enum'
                and 'static' in field.modifiers):
            return [owner], []

        if isinstance(node.value, ast.Call):
            named = self.find_type(identifier(node.value.func), field)
            return ([named] if named is not None else []), []
        if isinstance(node.value, ast.Name):
            method = enclosing_method(field)
            if method is not None:
                for parameter in parameters(method):
                    if parameter.arg == node.value.id:
                        return self.referenced_types(parameter.annotation,
                                                     field)
        return [], []

    def field_typed(self, field):
        """Returns the type of a field, which is not known unless the field
        is annotated or is set to a literal value."""
        typed = field_type(field)
        if typed.type is not None or typed.element is not None:
            return typed
        node = field.node
        value = node.value
        if isinstance(node, ast.AnnAssign) or isinstance(value, LITERALS) or (
                isinstance(value, ast.Constant) and value.value is not None):
            return EXTERNAL
        return None

    def add_declared_types(self, entity):
        node = entity.node
        if entity.type == 'field':
            # Field - Type, or the type that it is a collection of
            named, elements = self.field_types(entity)
            for related_entity in named:
                self.relate(IsOfType, entity, related_entity)
            for related_entity in elements:
                self.relate(IsCollectionOf, entity, related_entity)
        elif entity.type in METHOD_TYPES + ('constructor',):
            # Parameter
            for parameter in parameters(node):
                named, elements = self.referenced_types(parameter.annotation,
                                                        entity)
                for related_entity in named + elements:
                    self.relate(ParameterOfType, entity, related_entity)
            # ReturnType
            named, elements = self.referenced_types(node.returns, entity)
            for related_entity in named + elements:
                self.relate(HasReturnType, entity, related_entity)

    # Method - Overrides
    def add_overridden(self, entity):
        if entity.type == 'method':
            add_overrides(entity, self.relate, lambda method, member: True)

    # Field/Method/Constructor - Invokes, Instantiates, Assigns and Returns
    def add_usages(self, entity):
        node = entity.node
        owner = entity.relations['memberOf'][0] if entity.relations[
            'memberOf'] else None
        if entity.type == 'field':
            # A field of the class itself is set as the class is declared
            if 'static' in entity.modifiers:
                self.evaluate(node.value, Scope(entity, owner, returns=False))
        elif entity.type in ('method', 'constructor'):
            scope = Scope(entity, owner)
            for parameter in parameters(node):
                scope.variables[parameter.arg] = self.typed(
                    parameter.annotation, entity)

            decorators = decorator_names(node)
            arguments = node.args.posonlyargs + node.args.args
            if arguments and 'staticmethod' not in decorators:
                # The first parameter is the instance, or the class itself
                scope.variables[arguments[0].arg] = Typed(owner, None)
                if 'classmethod' in decorators or node.name == '__new__':
                    scope.classes[arguments[0].arg] = owner
            self.evaluate(node.body, scope)

    def evaluate(self, node, scope):
        """Adds the relations for what the code within a node uses. If the
        node is an expression, returns its type where that can be worked
        out."""
        if isinstance(node, list):
            for item in node:
                self.evaluate(item, scope)
            return None
        # What a local class contains belongs to it
        if not isinstance(node, ast.AST) or isinstance(node, ast.ClassDef):
            return None

        if isinstance(node, FUNCTIONS + (ast.Lambda,)):
            # The code of a nested function belongs to the member it is in
            self.evaluate(node.body, scope.within_function())
            return None
        if isinstance(node, ast.Call):
            return self.call(node, scope)
        if isinstance(node, ast.Attribute):
            return self.resolve(node, scope)[0]
        if isinstance(node, ast.Name):
            return self.name(node, scope)
        if isinstance(node, ast.Subscript):
            value = self.evaluate(node.value, scope)
            self.evaluate(node.slice, scope)
            return Typed(value.element, None) if value is not None else None
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            return self.assignment(node, scope)
        if isinstance(node, ast.Return):
            return self.return_statement(node, scope)
        if isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension)):
            iterable = self.evaluate(node.iter, scope)
            self.bind(node.target, self.element(iterable), scope)
            for attr in ('ifs', 'body', 'orelse'):
                self.evaluate(getattr(node, attr, None), scope)
            return None
        if isinstance(node, COMPREHENSIONS):
            # The variables of a comprehension are set before they are used
            self.evaluate(node.generators, scope)
            for attr in ('elt', 'key', 'value'):
                self.evaluate(getattr(node, attr, None), scope)
            return EXTERNAL
        if isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                value = self.evaluate(item.context_expr, scope)
                if item.optional_vars is not None:
                    self.bind(item.optional_vars, value, scope)
            self.evaluate(node.body, scope)
            return None
        if isinstance(node, ast.IfExp):
            self.evaluate(node.test, scope)
            body = self.evaluate(node.body, scope)
            orelse = self.evaluate(node.orelse, scope)
            return body or orelse
        if isinstance(node, ast.Await):
            return self.evaluate(node.value, scope)
        if isinstance(node, ast.NamedExpr):
            value = self.evaluate(node.value, scope)
            self.bind(node.target, value, scope)
            return value

        for child in ast.iter_child_nodes(node):
            self.evaluate(child, scope)
        if isinstance(node, LITERALS) or (
                isinstance(node, ast.Constant) and node.value is not None):
            return EXTERNAL
        return None

    @staticmethod
    def element(iterable):
        """Returns the type of each item of an iterable."""
        if iterable is None:
            return None
        return Typed(iterable.element, None)

    def name(self, node, scope):
        if node.id in scope.variables:
            return scope.variables[node.id]
        named = self.find_type(node.id, scope.member)
        if named is not None:
            return Typed(named, None)
        # A module is not part of the project's classes
        if node.id in self.names.get(scope.member.file, ()):
            return EXTERNAL
        return None

    def resolve(self, node, scope):
        """Returns the type of an attribute such as self.field, and the
        field that it refers to if it is one."""
        value = self.evaluate(node.value, scope)
        if value is None:
            return None, None
        if value.type is None:
            return EXTERNAL, None

        field = find_field(value.type, node.attr)
        if field is not None:
            return self.field_typed(field), field
        nested = find_members(value.type, node.attr, CLASS_TYPES)
        if nested:
            return Typed(nested[0], None), None
        return None, None

    def instantiate(self, node, class_entity, scope):
        self.relate(Instantiates, scope.member, class_entity)
        self.instantiations[id(node)] = class_entity
        return Typed(class_entity, None)

    def call(self, node, scope):
        """Relates the member to the method that it invokes or the class
        that it instantiates, and returns the type of the result."""
        function = node.func
        result = None
        if isinstance(function, ast.Name):
            if function.id in scope.classes:
                result = self.instantiate(node, scope.classes[function.id],
                                          scope)
            elif function.id not in scope.variables:
                named = self.find_type(function.id, scope.member)
                if named is not None:
                    result = self.instantiate(node, named, scope)
        elif isinstance(function, ast.Attribute):
            result = self.method_call(node, scope)
        else:
            self.evaluate(function, scope)

        for argument in node.args:
            self.evaluate(argument, scope)
        for keyword in node.keywords:
            self.evaluate(keyword.value, scope)
        return result

    def method_call(self, node, scope):
        function = node.func
        name = function.attr
        if is_super(function.value):
            # The class is created by the __new__ that it inherits
            if name == '__new__' and scope.owner is not None:
                return self.instantiate(node, scope.owner, scope)
            receiver = EXTERNAL
            receivers = (scope.owner.relations['extends']
                         + scope.owner.relations['implements'])
        else:
            receiver = self.evaluate(function.value, scope)
            receivers = ([receiver.type] if receiver is not None
                         and receiver.type is not None else [])

        if receiver is None:
            # Nothing is known of what the method is called on, so it may be
            # a class within a module, or the only method with the name
            named = self.find_type(name, scope.member)
            if named is not None:
                return self.instantiate(node, named, scope)
            method = find_unique(name, self.first_pass_dict, METHOD_TYPES)
        else:
            method = None
            for class_entity in receivers:
                methods = find_members(class_entity, name, METHOD_TYPES)
                if methods:
                    method = methods[0]
                    break
                nested = find_members(class_entity, name, CLASS_TYPES)
                if nested:
                    return self.instantiate(node, nested[0], scope)

        if method is not None:
            self.relate(Invokes, scope.member, method)
            return self.typed(method.node.returns, method)
        if receiver is None:
            return None
        # What a method of a collection returns is likely to be one of the
        # elements that it holds
        return Typed(receiver.element, receiver.element)

    def bind(self, target, typed, scope, value=None):
        """Sets the type of the variable that a value is assigned to, or
        relates the member to the field that it is assigned to."""
        if isinstance(target, ast.Name):
            scope.variables[target.id] = typed
        elif isinstance(target, ast.Attribute):
            _, field = self.resolve(target, scope)
            if field is None:
                return
            if scope.member.type != 'field':
                self.relate(Assigns, scope.member, field)
            # A field instantiates the class that it is set to a new one of
            if id(value) in self.instantiations:
                self.relate(Instantiates, field,
                            self.instantiations[id(value)])
        elif isinstance(target, (ast.Tuple, ast.List)):
            for item in target.elts:
                self.bind(item, None, scope)
        else:
            self.evaluate(target, scope)

    def assignment(self, node, scope):
        value = self.evaluate(node.value, scope)
        if isinstance(node, ast.AnnAssign):
            value = self.typed(node.annotation, scope.member) or value
        targets = (node.targets if isinstance(node, ast.Assign)
                   else [node.target])
        for target in targets:
            self.bind(target, value, scope, node.value)
        return None

    def return_statement(self, node, scope):
        if scope.returns and isinstance(node.value, ast.Attribute):
            _, field = self.resolve(node.value, scope)
            if field is not None:
                self.relate(Returns, scope.member, field)
        self.evaluate(node.value, scope)
        return None


def build_python_graph(files, display=False):
    entities = []
    relations = []
    first_pass_dict = {}
    imports = {}
    names = {}

    # Initial Pass
    for file in files:
        file_entities, file_relations = first_pass(file, first_pass_dict)
        entities.extend(file_entities)
        relations.extend(file_relations)
        full_file_name = os.path.join(file.relative_dir, file.file_name)
        imports[full_file_name] = imports_of(file.ast)
        names[full_file_name] = imported_names(file.ast)

        if display:
            print_graph(file_entities, file_relations)

    PythonSecondPass(entities, relations, first_pass_dict, imports, names)

    if display:
        print_graph(entities, relations)

    return {'entities': entities, 'relations': relations}
