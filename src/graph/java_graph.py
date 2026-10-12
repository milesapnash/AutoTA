import os.path

from src.filters.java_filter import (
    child_of_type, modifiers_of, supertype_nodes, text, type_name)
from src.graph.er_classes import (
    AbstractClass, AbstractMethod, Assigns, Class, Constructor, Extends,
    Field, Has, HasReturnType, Implements, Instantiates, Interface, Invokes,
    IsCollectionOf, IsOfType, Method, Overrides, ParameterOfType, Returns)
from src.graph.graph_display import print_graph
from src.graph.utils import (
    CLASS_TYPES, EXTERNAL, METHOD_TYPES, Typed, add_node_to_dict,
    add_overrides, enclosing_classes, field_type, find_field, find_in_dict,
    find_members, find_unique, relation_adder, supertypes)

TYPE_DECLARATIONS = ('class_declaration', 'interface_declaration',
                     'enum_declaration', 'record_declaration')
FIELD_DECLARATIONS = ('field_declaration', 'constant_declaration')
CONSTRUCTOR_DECLARATIONS = ('constructor_declaration',
                            'compact_constructor_declaration')
# The members of an interface, and the constants of an enum, are implicitly
# public, static and final
CONSTANT_MODIFIERS = {'public', 'static', 'final'}
# The components of a record are implicitly private and final
COMPONENT_MODIFIERS = {'private', 'final'}
# Generic types that hold a single value rather than a collection of them
WRAPPERS = {'Optional'}
# Expressions whose value is not an instance of a class in the project
EXTERNAL_EXPRESSIONS = ('binary_expression', 'unary_expression',
                        'update_expression', 'instanceof_expression',
                        'class_literal')
# Nodes that declare a variable with a type and a name
PATTERNS = ('type_pattern', 'record_pattern_component')


def is_anonymous_class(node):
    return (node.type == 'object_creation_expression'
            and child_of_type(node, 'class_body') is not None)


def walk(root):
    """Yields root and every named node within it. Local and anonymous
    classes are yielded but not entered, as what they contain belongs to
    them."""
    stack = [root] if root is not None else []
    while stack:
        node = stack.pop()
        yield node
        if node.type in TYPE_DECLARATIONS:
            continue
        stack.extend(child for child in reversed(node.named_children)
                     if child.type != 'class_body')


def code_of(member):
    """Returns the part of a member in which code can appear."""
    if member.type == 'variable_declarator':
        return member.child_by_field_name('value')
    if member.type == 'enum_constant':
        return member.child_by_field_name('arguments')
    return member.child_by_field_name('body')


def named_types(node):
    """Yields the name of every type within a node, such as the arguments
    of a generic type."""
    stack = [node]
    while stack:
        current = stack.pop()
        if current.type in ('type_identifier', 'scoped_type_identifier'):
            yield type_name(current)
        else:
            stack.extend(reversed(current.named_children))


def type_parts(type_node, array=False):
    """Returns the name of a type, the names of its type arguments however
    deeply nested, and whether it is an array."""
    while type_node.type in ('array_type', 'annotated_type'):
        if type_node.type == 'array_type':
            array = True
            type_node = type_node.child_by_field_name('element')
        else:
            type_node = type_node.named_children[-1]

    arguments = child_of_type(type_node, 'type_arguments')
    return (type_name(type_node),
            list(named_types(arguments)) if arguments is not None else [],
            array)


def parameters_of(node):
    """Returns the name, type and whether it takes several arguments of
    each parameter of a method, constructor or lambda expression."""
    parameters = node.child_by_field_name('parameters')
    if parameters is None:
        return []
    if parameters.type == 'identifier':
        # A lambda expression with a single parameter and no brackets
        return [(text(parameters), None, False)]

    found = []
    for parameter in parameters.named_children:
        if parameter.type == 'identifier':
            found.append((text(parameter), None, False))
        elif parameter.type == 'formal_parameter':
            found.append((text(parameter.child_by_field_name('name')),
                          parameter.child_by_field_name('type'), False))
        elif parameter.type == 'spread_parameter':
            declared = [child for child in parameter.named_children
                        if child.type not in ('modifiers',
                                              'variable_declarator')]
            declarator = child_of_type(parameter, 'variable_declarator')
            found.append((text(declarator.child_by_field_name('name')),
                          declared[0] if declared else None, True))
    return found


def arity(method):
    return len(parameters_of(method.node))


def overridable(method, member):
    return ('static' not in method.info['modifiers']
            and not member.info['modifiers'] & {'static', 'private'}
            and arity(method) == arity(member))


def imports_of(root):
    """Returns the path of each import in a file, with whether it is
    static and whether it imports everything at that path."""
    imports = []
    for node in root.named_children:
        if node.type == 'import_declaration':
            path = child_of_type(node, 'scoped_identifier', 'identifier')
            imports.append((text(path),
                            child_of_type(node, 'static') is not None,
                            child_of_type(node, 'asterisk') is not None))
    return imports


class FirstPass:
    """Creates the entities declared in a file, and the Has relations
    between each of them and the class it belongs to."""

    def __init__(self, file, first_pass_dict):
        package = child_of_type(file.ast, 'package_declaration')
        if package is not None:
            package = text(child_of_type(package, 'scoped_identifier',
                                         'identifier'))
        self.location = {
            'package': package,
            'file': os.path.join(file.relative_path, file.file_name)}
        self.first_pass_dict = first_pass_dict
        self.entities = []
        self.relations = []

        for type_node in file.ast.named_children:
            self.add_type(type_node)

    def add(self, entity_type, info, node, owner=None):
        entity = entity_type(info=info, node=node, **self.location)
        self.entities.append(entity)
        add_node_to_dict(self.first_pass_dict, info['name'], entity)
        if owner is not None:
            self.relations.append(Has(owner, entity))
        return entity

    def add_type(self, node, owner=None):
        if node.type == 'interface_declaration':
            entity_type = Interface
        elif node.type == 'class_declaration':
            entity_type = (AbstractClass if 'abstract' in modifiers_of(node)
                           else Class)
        elif node.type in ('enum_declaration', 'record_declaration'):
            # An enum is a class whose constants are fields of its own type,
            # and a record is one whose components are its fields
            entity_type = Class
        else:
            return

        name = text(node.child_by_field_name('name'))
        entity = self.add(entity_type, {'name': name}, node, owner)

        if node.type == 'record_declaration':
            for component in node.child_by_field_name(
                    'parameters').named_children:
                if component.type == 'formal_parameter':
                    info = {'modifiers': COMPONENT_MODIFIERS,
                            'name': text(
                                component.child_by_field_name('name')),
                            'type': type_name(
                                component.child_by_field_name('type'))}
                    self.add(Field, info, component, entity)
        self.add_members(entity, node.child_by_field_name('body'))

    def add_anonymous_class(self, owner, node, supertype):
        info = {'name': f'Anonymous {supertype}', 'supertype': supertype}
        entity = self.add(Class, info, node, owner)
        self.add_members(entity, child_of_type(node, 'class_body'))

    def add_members(self, owner, body):
        owner_name = owner.info['name']
        for member in body.named_children if body is not None else []:
            if member.type in TYPE_DECLARATIONS:
                self.add_type(member, owner)
            elif member.type == 'enum_body_declarations':
                # The members of an enum follow its constants
                self.add_members(owner, member)
            elif member.type == 'enum_constant':
                info = {'modifiers': CONSTANT_MODIFIERS,
                        'name': text(member.child_by_field_name('name')),
                        'type': owner_name}
                self.add(Field, info, member, owner)
                self.add_inner_classes(owner, member)
                # A constant with a body is an anonymous subclass of the enum
                if child_of_type(member, 'class_body') is not None:
                    self.add_anonymous_class(owner, member, owner_name)
            elif member.type == 'method_declaration':
                modifiers = modifiers_of(member)
                # A method of an interface is abstract unless it has a body,
                # as default, static and private methods do
                abstract = 'abstract' in modifiers or (
                    owner.type == 'interface'
                    and member.child_by_field_name('body') is None)
                info = {'modifiers': modifiers,
                        'name': text(member.child_by_field_name('name'))}
                self.add(AbstractMethod if abstract else Method, info,
                         member, owner)
                self.add_inner_classes(owner, member)
            elif member.type in FIELD_DECLARATIONS:
                modifiers = modifiers_of(member)
                if owner.type == 'interface':
                    modifiers = modifiers | CONSTANT_MODIFIERS
                declared = member.child_by_field_name('type')
                for field in member.children_by_field_name('declarator'):
                    info = {'modifiers': modifiers,
                            'name': text(field.child_by_field_name('name')),
                            'type': type_name(declared)}
                    self.add(Field, info, field, owner)
                    self.add_inner_classes(owner, field)
            elif member.type in CONSTRUCTOR_DECLARATIONS:
                info = {'modifiers': modifiers_of(member),
                        'name': f'{owner_name} Constructor'}
                self.add(Constructor, info, member, owner)
                self.add_inner_classes(owner, member)

    def add_inner_classes(self, owner, member):
        """Adds the local and anonymous classes declared within a member."""
        for node in walk(code_of(member)):
            if node.type in TYPE_DECLARATIONS:
                self.add_type(node, owner)
            elif is_anonymous_class(node):
                self.add_anonymous_class(
                    owner, node, type_name(node.child_by_field_name('type')))


def supertype_names(entity):
    if 'supertype' in entity.info:
        return [entity.info['supertype']]
    return [type_name(supertype) for supertype in supertype_nodes(
        entity.node, 'superclass', 'super_interfaces', 'extends_interfaces')]


class Scope:
    """The member that a piece of code belongs to, and the types of the
    parameters and local variables that the code can refer to."""

    def __init__(self, member, owner, variables, return_type=None,
                 returns=True):
        self.member = member
        self.owner = owner
        self.variables = variables
        self.return_type = return_type
        # Whether a return statement in the code returns from the member
        self.returns = returns

    def within_lambda(self):
        return Scope(self.member, self.owner, self.variables, returns=False)


class SecondPass:
    """Adds the relations between the entities found by the first pass."""

    def __init__(self, entities, relations, first_pass_dict, imports):
        self.entities = entities
        self.first_pass_dict = first_pass_dict
        self.imports = imports
        self.relate = relation_adder(relations)
        self.anonymous_classes = {
            self.position(entity, entity.node): entity
            for entity in entities if is_anonymous_class(entity.node)}
        self.evaluators = {
            'lambda_expression': self.lambda_expression,
            'method_reference': self.method_reference,
            'ternary_expression': self.ternary_expression,
            'parenthesized_expression': self.parenthesized_expression,
            'assignment_expression': self.assignment,
            'return_statement': self.return_statement,
            'local_variable_declaration': self.variable_declaration,
            'enhanced_for_statement': self.enhanced_for,
            'cast_expression': self.cast,
            'method_invocation': self.method_invocation,
            'object_creation_expression': self.creator,
            'array_creation_expression': self.array_creator,
            'explicit_constructor_invocation': self.constructor_invocation,
            'array_access': self.array_access,
            'field_access': self.name,
            'identifier': self.name,
            'this': self.name}

        # Each step relies on the relations added by those before it, and
        # the last adds an entity for each lambda expression that it finds
        declared = list(entities)
        for step in (self.add_supertypes, self.add_declared_types,
                     self.add_overridden, self.add_usages):
            for entity in declared:
                step(entity)

    @staticmethod
    def position(origin, node):
        """Identifies a node by where it is in the project."""
        return origin.file, node.start_byte

    def is_imported(self, origin, entity):
        name = entity.info['name']
        for path, static, wildcard in self.imports.get(origin.file, ()):
            if static or entity.package is None:
                continue
            if wildcard:
                if path == entity.package:
                    return True
            elif (path.startswith(entity.package + '.')
                  and path.endswith('.' + name)):
                return True
        return False

    def find_type(self, name, origin):
        if name is None:
            return None
        return find_in_dict(name, self.first_pass_dict, origin,
                            types=CLASS_TYPES, imported=self.is_imported)

    def referenced_types(self, type_node, origin, array=False):
        """Returns the classes that a declared type refers to: those that it
        names, and those that it is an array or a collection of."""
        if type_node is None:
            return [], []

        name, arguments, array = type_parts(type_node, array)
        named = self.find_type(name, origin)
        named = [named] if named is not None else []
        arguments = [argument for argument in
                     (self.find_type(argument, origin)
                      for argument in arguments)
                     if argument is not None]

        if name in WRAPPERS:
            return arguments[:1], arguments[1:]
        if array:
            return [], named + arguments
        return named, arguments

    def typed(self, type_node, origin, array=False):
        named, elements = self.referenced_types(type_node, origin, array)
        return Typed(named[0] if named else None,
                     elements[0] if elements else None)

    def return_type(self, method):
        if method.node.type == 'method_declaration':
            return self.typed(method.node.child_by_field_name('type'), method)
        return None

    # Class - Extends, or Implements if the supertype is an interface
    def add_supertypes(self, entity):
        if entity.type not in CLASS_TYPES:
            return
        for supertype in supertype_names(entity):
            related_entity = self.find_type(supertype, entity)
            if related_entity is None:
                continue
            if (related_entity.type == 'interface'
                    and entity.type != 'interface'):
                self.relate(Implements, entity, related_entity)
            else:
                self.relate(Extends, entity, related_entity)

    def add_declared_types(self, entity):
        node = entity.node
        if entity.type == 'field':
            # Field - Type, or the type that it is a collection of
            if node.type == 'enum_constant':
                named = [self.find_type(entity.info['type'], entity)]
                elements = []
            else:
                # Several fields may be declared together with one type
                declaration = (node.parent if node.type ==
                               'variable_declarator' else node)
                named, elements = self.referenced_types(
                    declaration.child_by_field_name('type'), entity,
                    node.child_by_field_name('dimensions') is not None)
            for related_entity in named:
                if related_entity is not None:
                    self.relate(IsOfType, entity, related_entity)
            for related_entity in elements:
                self.relate(IsCollectionOf, entity, related_entity)
        elif entity.type in METHOD_TYPES + ('constructor',):
            # AbstractMethod/Method/Constructor - Parameter
            for _, declared, _ in parameters_of(node):
                named, elements = self.referenced_types(declared, entity)
                for related_entity in named + elements:
                    self.relate(ParameterOfType, entity, related_entity)
            # AbstractMethod/Method - ReturnType
            if entity.type in METHOD_TYPES:
                named, elements = self.referenced_types(
                    node.child_by_field_name('type'), entity)
                for related_entity in named + elements:
                    self.relate(HasReturnType, entity, related_entity)

    # Method - Overrides
    def add_overridden(self, entity):
        if entity.type == 'method':
            add_overrides(entity, self.relate, overridable)

    # Field/Method/Constructor - Invokes, Instantiates, Assigns and Returns
    def add_usages(self, entity):
        owners = entity.relations['composes']
        if entity.type == 'field':
            scope = Scope(entity, owners[0], {}, returns=False)
            target = field_type(entity)
        elif entity.type in ('method', 'constructor'):
            scope = Scope(entity, owners[0], self.variables(entity),
                          self.return_type(entity))
            target = None
        else:
            return

        try:
            self.evaluate(code_of(entity.node), scope, target)
        except RecursionError:
            # An expression nested too deeply to follow is left out
            pass

    def variables(self, entity):
        """Returns the types of the parameters and local variables of a
        method or constructor, wherever in it they are declared."""
        variables = {}
        for name, declared, varargs in parameters_of(entity.node):
            variables[name] = self.typed(declared, entity, varargs)

        for node in walk(code_of(entity.node)):
            if node.type == 'local_variable_declaration':
                declared = node.child_by_field_name('type')
                for declarator in node.children_by_field_name('declarator'):
                    name = text(declarator.child_by_field_name('name'))
                    variables[name] = self.typed(
                        declared, entity,
                        declarator.child_by_field_name(
                            'dimensions') is not None)
            elif node.type in ('enhanced_for_statement', 'resource',
                               'formal_parameter'):
                name = node.child_by_field_name('name')
                if name is not None:
                    variables[text(name)] = self.typed(
                        node.child_by_field_name('type'), entity)
            elif node.type == 'catch_formal_parameter':
                caught = child_of_type(node, 'catch_type').named_children
                variables[text(node.child_by_field_name('name'))] = (
                    self.typed(caught[0], entity) if caught else EXTERNAL)
            elif node.type == 'instanceof_expression':
                name = node.child_by_field_name('name')
                if name is not None:
                    variables[text(name)] = self.typed(
                        node.child_by_field_name('right'), entity)
            elif node.type in PATTERNS:
                parts = [child for child in node.named_children
                         if child.type != 'modifiers']
                if len(parts) == 2 and parts[1].type == 'identifier':
                    variables[text(parts[1])] = self.typed(parts[0], entity)
        return variables

    def evaluate(self, node, scope, target=None):
        """Adds the relations for what the code within a node uses. If the
        node is an expression, returns its type where that can be worked
        out. The target is the type expected where the expression appears,
        which is what a lambda expression there would implement."""
        # What a local class contains belongs to it
        if node is None or node.type in TYPE_DECLARATIONS:
            return None

        evaluator = self.evaluators.get(node.type)
        if evaluator is not None:
            return evaluator(node, scope, target)

        for child in node.named_children:
            self.evaluate(child, scope)
        if (node.type in EXTERNAL_EXPRESSIONS or node.type.endswith(
                '_literal') and node.type != 'null_literal'):
            return EXTERNAL
        return None

    def name(self, node, scope, target=None):
        return self.resolve(node, scope)[0]

    def resolve(self, node, scope):
        """Returns the type of a name such as count, this.field or
        Outer.CONSTANT, and the field that it refers to if it is one."""
        owner = scope.owner
        if node.type == 'this':
            return Typed(owner, None), None

        if node.type == 'identifier':
            name = text(node)
            if name in scope.variables:
                return scope.variables[name], None
            for class_entity in [owner] + enclosing_classes(owner):
                field = find_field(class_entity, name)
                if field is not None:
                    return field_type(field), field
            return self.class_named(name, scope), None

        receiver_node = node.child_by_field_name('object')
        field_node = node.child_by_field_name('field')
        if field_node.type == 'this':
            # The instance of an outer class, as in Outer.this
            return self.evaluate(receiver_node, scope), None

        name = text(field_node)
        if receiver_node.type == 'super':
            receiver = Typed(owner, None)
        else:
            receiver = self.evaluate(receiver_node, scope)
        if receiver is None:
            # The last name of a package or of nested classes
            return self.class_named(name, scope), None
        if receiver.type is None:
            return EXTERNAL, None

        field = find_field(receiver.type, name)
        if field is not None:
            return field_type(field), field
        return self.class_named(name, scope), None

    def class_named(self, name, scope):
        """Returns the type that a name refers to when it is not that of a
        variable or field. One that starts with a capital is taken to be a
        class from outside the project, such as System."""
        named = self.find_type(name, scope.member)
        if named is not None:
            return Typed(named, None)
        return EXTERNAL if name[:1].isupper() else None

    def field_referenced(self, node, scope):
        """Returns the field that an expression refers to, if it is one."""
        if node is not None and node.type in ('identifier', 'field_access'):
            return self.resolve(node, scope)[1]
        return None

    def find_method(self, class_entity, name, arguments):
        methods = find_members(class_entity, name, METHOD_TYPES)
        for method in methods:
            if arity(method) == arguments:
                return method
        return methods[0] if methods else None

    def constructor(self, class_entity, arguments):
        if class_entity is None:
            return None
        constructors = [member for member in class_entity.relations['has']
                        if member.type == 'constructor']
        for constructor in constructors:
            if arity(constructor) == arguments:
                return constructor
        return constructors[0] if constructors else None

    def method_invocation(self, node, scope, target=None):
        """Relates the member to the method that it invokes, and returns the
        type of what the method returns."""
        owner = scope.owner
        receiver_node = node.child_by_field_name('object')
        if receiver_node is None:
            # A method called by name alone is declared by the class, a
            # class that it inherits from or one that it is declared within
            receiver = Typed(owner, None)
            receivers = [owner] + enclosing_classes(owner)
        elif receiver_node.type == 'super':
            receiver = EXTERNAL
            receivers = (owner.relations['extends']
                         + owner.relations['implements'])
        else:
            receiver = self.evaluate(receiver_node, scope)
            receivers = ([receiver.type] if receiver is not None
                         and receiver.type is not None else [])

        name = text(node.child_by_field_name('name'))
        arguments = node.child_by_field_name('arguments').named_children
        method = None
        if receiver is None:
            # Nothing is known of what the method is called on, so it is
            # taken to be the only method with the name, if there is one
            method = find_unique(name, self.first_pass_dict, METHOD_TYPES)
        for class_entity in receivers:
            method = self.find_method(class_entity, name, len(arguments))
            if method is not None:
                break

        if method is not None:
            self.relate(Invokes, scope.member, method)
        self.arguments(arguments, method, scope)

        if method is not None:
            return self.return_type(method)
        if receiver is None:
            return None
        # What a method of a collection returns is likely to be one of the
        # elements that it holds
        return Typed(receiver.element, receiver.element)

    def arguments(self, arguments, callee, scope):
        """Evaluates the arguments of a call, where each is expected to be
        of the type of the parameter that it is passed as."""
        parameters = parameters_of(callee.node) if callee is not None else []
        for index, argument in enumerate(arguments):
            target = None
            if index < len(parameters) and parameters[index][1] is not None:
                _, declared, varargs = parameters[index]
                target = self.typed(declared, callee, varargs)
            self.evaluate(argument, scope, target)

    def creator(self, node, scope, target=None):
        if is_anonymous_class(node):
            class_entity = self.anonymous_classes.get(
                self.position(scope.member, node))
        else:
            class_entity = self.find_type(
                type_name(node.child_by_field_name('type')), scope.member)

        arguments = node.child_by_field_name('arguments')
        arguments = arguments.named_children if arguments is not None else []
        if class_entity is not None:
            self.relate(Instantiates, scope.member, class_entity)
        self.arguments(arguments,
                       self.constructor(class_entity, len(arguments)), scope)
        return Typed(class_entity, None)

    def array_creator(self, node, scope, target=None):
        for child in node.named_children:
            self.evaluate(child, scope)
        return self.typed(node.child_by_field_name('type'), scope.member,
                          array=True)

    def constructor_invocation(self, node, scope, target=None):
        """Evaluates the arguments passed on to another constructor."""
        class_entity = scope.owner
        if node.child_by_field_name('constructor').type == 'super':
            parents = class_entity.relations['extends']
            class_entity = parents[0] if parents else None
        arguments = node.child_by_field_name('arguments').named_children
        self.arguments(arguments,
                       self.constructor(class_entity, len(arguments)), scope)
        return None

    def array_access(self, node, scope, target=None):
        array = self.evaluate(node.child_by_field_name('array'), scope)
        self.evaluate(node.child_by_field_name('index'), scope)
        return Typed(array.element, None) if array is not None else None

    def parenthesized_expression(self, node, scope, target=None):
        return self.evaluate(node.named_children[0], scope, target)

    def ternary_expression(self, node, scope, target=None):
        self.evaluate(node.child_by_field_name('condition'), scope)
        consequence = self.evaluate(
            node.child_by_field_name('consequence'), scope, target)
        alternative = self.evaluate(
            node.child_by_field_name('alternative'), scope, target)
        return consequence or alternative

    def cast(self, node, scope, target=None):
        self.evaluate(node.child_by_field_name('value'), scope)
        return self.typed(node.child_by_field_name('type'), scope.member)

    def assignment(self, node, scope, target=None):
        left = node.child_by_field_name('left')
        right = node.child_by_field_name('right')
        field = self.field_referenced(left, scope)
        assigned = self.evaluate(left, scope)
        value = self.evaluate(right, scope, assigned)
        if field is not None:
            if scope.member.type != 'field':
                self.relate(Assigns, scope.member, field)
            # A field instantiates the class that it is set to a new one of
            if (right.type == 'object_creation_expression'
                    and value.type is not None):
                self.relate(Instantiates, field, value.type)
        return assigned

    def return_statement(self, node, scope, target=None):
        returned = node.named_children[0] if node.named_children else None
        if not scope.returns:
            self.evaluate(returned, scope)
            return None
        field = self.field_referenced(returned, scope)
        if field is not None:
            self.relate(Returns, scope.member, field)
        self.evaluate(returned, scope, scope.return_type)
        return None

    def variable_declaration(self, node, scope, target=None):
        declared_node = node.child_by_field_name('type')
        declared = self.typed(declared_node, scope.member)
        for declarator in node.children_by_field_name('declarator'):
            value = self.evaluate(declarator.child_by_field_name('value'),
                                  scope, declared)
            # The type of a var is that of the value it is first given
            if type_name(declared_node) == 'var' and value is not None:
                name = text(declarator.child_by_field_name('name'))
                scope.variables[name] = value
        return None

    def enhanced_for(self, node, scope, target=None):
        iterable = self.evaluate(node.child_by_field_name('value'), scope)
        declared = type_name(node.child_by_field_name('type'))
        if declared == 'var' and iterable is not None:
            name = text(node.child_by_field_name('name'))
            scope.variables[name] = Typed(iterable.element, None)
        self.evaluate(node.child_by_field_name('body'), scope)
        return None

    def functional_method(self, target):
        """Returns the method that a lambda expression implements, where
        the target is the type expected of the expression."""
        if (target is None or target.type is None
                or target.type.type != 'interface'):
            return None
        abstract_methods = [
            member for interface in [target.type] + supertypes(target.type)
            for member in interface.relations['has']
            if member.type == 'abstractMethod']
        return abstract_methods[0] if len(abstract_methods) == 1 else None

    def add_lambda(self, node, scope, abstract_method):
        """Adds a class for a lambda expression or method reference, with
        the one method that it implements, and returns that method."""
        interface = abstract_method.relations['composes'][0]
        location = {'node': node, 'package': scope.member.package,
                    'file': scope.member.file}
        lambda_class = Class(
            info={'name': f'Lambda {interface.info["name"]}'}, **location)
        method = Method(info={'modifiers': {'public'},
                              'name': abstract_method.info['name']},
                        **location)
        self.entities.extend([lambda_class, method])

        self.relate(Has, scope.owner, lambda_class)
        self.relate(Has, lambda_class, method)
        self.relate(Implements, lambda_class, interface)
        self.relate(Overrides, method, abstract_method)
        self.relate(Instantiates, scope.member, lambda_class)
        return method

    def lambda_expression(self, node, scope, target=None):
        body = node.child_by_field_name('body')
        abstract_method = self.functional_method(target)
        if abstract_method is None:
            # Without an interface in the project for the lambda expression
            # to implement, its code belongs to the member it is written in
            self.evaluate(body, scope.within_lambda())
            return None

        method = self.add_lambda(node, scope, abstract_method)
        variables = dict(scope.variables)
        implemented = parameters_of(abstract_method.node)
        for parameter, declared in zip(parameters_of(node), implemented):
            # A parameter without a type has that of the method implemented
            name, declared_type, varargs = parameter
            origin = scope.member
            if declared_type is None:
                _, declared_type, varargs = declared
                origin = abstract_method
            variables[name] = self.typed(declared_type, origin, varargs)

        return_type = self.return_type(abstract_method)
        self.evaluate(body, Scope(method, scope.owner, variables,
                                  return_type), return_type)
        return Typed(method.relations['composes'][0], None)

    def method_reference(self, node, scope, target=None):
        abstract_method = self.functional_method(target)
        member = scope.member
        result = None
        if abstract_method is not None:
            member = self.add_lambda(node, scope, abstract_method)
            result = Typed(member.relations['composes'][0], None)

        # Either a type or an expression comes before the method's name
        qualifier = node.children[0]
        if qualifier.type == 'super':
            parents = scope.owner.relations['extends']
            receiver = Typed(parents[0] if parents else None, None)
        elif qualifier.type in self.evaluators:
            receiver = self.evaluate(qualifier, scope)
        else:
            receiver = self.typed(qualifier, scope.member)

        if child_of_type(node, 'new') is not None:
            if receiver is not None and receiver.type is not None:
                self.relate(Instantiates, member, receiver.type)
            return result

        name = text(node.named_children[-1])
        referenced = None
        if receiver is None:
            referenced = find_unique(name, self.first_pass_dict,
                                     METHOD_TYPES)
        elif receiver.type is not None:
            referenced = self.find_method(receiver.type, name, None)
        if referenced is not None:
            self.relate(Invokes, member, referenced)
        return result


def build_java_graph(files, display=False):
    entities = []
    relations = []
    first_pass_dict = {}
    imports = {}

    # Initial Pass
    for file in files:
        file_pass = FirstPass(file, first_pass_dict)
        entities.extend(file_pass.entities)
        relations.extend(file_pass.relations)
        imports[file_pass.location['file']] = imports_of(file.ast)

        if display:
            print_graph(file_pass.entities, file_pass.relations)

    SecondPass(entities, relations, first_pass_dict, imports)

    if display:
        print_graph(entities, relations)

    return {'entities': entities, 'relations': relations}
