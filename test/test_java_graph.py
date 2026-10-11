import unittest

from src.entity_relations.java_graph import build_java_graph
from src.project.review_file import ReviewFile


def build(*sources):
    files = [ReviewFile('./', '', f'Example{index}.java', contents=code)
             for index, code in enumerate(sources)]
    return build_java_graph(files)


def described(graph):
    return {(entity.type, entity.info['name'])
            for entity in graph['entities']}


def related(graph, relation_type):
    return {(relation.entity_from.info['name'],
             relation.entity_to.info['name'])
            for relation in graph['relations']
            if relation.relation_type == relation_type}


def qualified(entity):
    """Names a member along with the class that it belongs to."""
    owners = entity.relations['composes']
    if owners and entity.type not in ('class', 'abstractClass', 'interface'):
        return f'{owners[0].info["name"]}.{entity.info["name"]}'
    return entity.info['name']


def related_members(graph, relation_type):
    return {(qualified(relation.entity_from), qualified(relation.entity_to))
            for relation in graph['relations']
            if relation.relation_type == relation_type}


def entity_named(graph, name):
    return next(entity for entity in graph['entities']
                if entity.info['name'] == name)


class TestInterfaces(unittest.TestCase):
    def test_constant_is_a_static_field(self):
        graph = build('''
        interface Limits {
            int MAX = 10;
            void check();
        }
        ''')

        self.assertEqual(described(graph), {('interface', 'Limits'),
                                            ('field', 'MAX'),
                                            ('abstractMethod', 'check')})
        self.assertLessEqual({'public', 'static', 'final'},
                             entity_named(graph, 'MAX').info['modifiers'])

    def test_method_with_a_body_is_not_abstract(self):
        graph = build('''
        interface Shape {
            double area();
            default String describe() { return "shape"; }
            static Shape unit() { return null; }
        }
        ''')

        self.assertEqual(described(graph), {('interface', 'Shape'),
                                            ('abstractMethod', 'area'),
                                            ('method', 'describe'),
                                            ('method', 'unit')})


class TestInnerClasses(unittest.TestCase):
    def test_nested_class_belongs_to_outer_class(self):
        graph = build('''
        class Pizza {
            static class Builder {
                Pizza build() { return new Pizza(); }
            }
        }
        ''')

        self.assertEqual(described(graph), {('class', 'Pizza'),
                                            ('class', 'Builder'),
                                            ('method', 'build')})
        self.assertEqual(related(graph, 'has'), {('Pizza', 'Builder'),
                                                 ('Builder', 'build')})

    def test_local_class_is_included(self):
        graph = build('''
        class Outer {
            void run() {
                class Local {
                    void help() {}
                }
            }
        }
        ''')

        self.assertIn(('class', 'Local'), described(graph))
        self.assertIn(('Local', 'help'), related(graph, 'has'))

    def test_anonymous_class_implements_its_interface(self):
        graph = build('''
        interface Strategy {
            void algorithm();
        }

        class Context {
            private Strategy strategy = new Strategy() {
                public void algorithm() {}
            };
        }
        ''')

        self.assertIn(('class', 'Anonymous Strategy'), described(graph))
        self.assertEqual(related(graph, 'implements'),
                         {('Anonymous Strategy', 'Strategy')})
        self.assertEqual(related(graph, 'overrides'),
                         {('algorithm', 'algorithm')})
        self.assertEqual(related(graph, 'instantiates'),
                         {('strategy', 'Anonymous Strategy')})

    def test_anonymous_class_extends_a_class(self):
        graph = build('''
        class Base {}

        class Factory {
            Base make() { return new Base() {}; }
        }
        ''')

        self.assertEqual(related(graph, 'extends'),
                         {('Anonymous Base', 'Base')})

    def test_code_in_anonymous_class_belongs_to_its_methods(self):
        graph = build('''
        interface Task {
            void run();
        }

        class Tool {}

        class Scheduler {
            Task make() {
                return new Task() {
                    public void run() { new Tool(); }
                };
            }
        }
        ''')

        self.assertEqual(related(graph, 'instantiates'),
                         {('make', 'Anonymous Task'), ('run', 'Tool')})


class TestEnums(unittest.TestCase):
    def test_enum_is_a_class_with_a_field_for_each_constant(self):
        graph = build('''
        interface Named {
            String label();
        }

        enum Colour implements Named {
            RED, GREEN;

            private int code;

            public String label() { return "colour"; }
        }
        ''')

        self.assertLessEqual({('class', 'Colour'), ('field', 'RED'),
                              ('field', 'GREEN'), ('field', 'code'),
                              ('method', 'label')}, described(graph))
        self.assertEqual(related(graph, 'implements'),
                         {('Colour', 'Named')})
        self.assertEqual(related(graph, 'isOfType'),
                         {('RED', 'Colour'), ('GREEN', 'Colour')})

    def test_constant_with_a_body_is_an_anonymous_subclass(self):
        graph = build('''
        enum Operation {
            NEGATE {
                int apply(int x) { return -x; }
            };

            abstract int apply(int x);
        }
        ''')

        self.assertLessEqual({('class', 'Anonymous Operation'),
                              ('abstractMethod', 'apply'),
                              ('method', 'apply')}, described(graph))
        self.assertEqual(related(graph, 'extends'),
                         {('Anonymous Operation', 'Operation')})
        self.assertEqual(related(graph, 'overrides'), {('apply', 'apply')})


class TestRelations(unittest.TestCase):
    def test_new_expression_instantiates_class(self):
        graph = build('''
        class Engine {}

        class Car {
            private Engine spare = new Engine();
            private Engine engine;

            Car() { engine = new Engine(); }

            Engine replace() {
                new Engine();
                return new Engine();
            }
        }
        ''')

        # A field instantiates the class that it is set to a new one of
        self.assertEqual(related(graph, 'instantiates'),
                         {('spare', 'Engine'), ('Car Constructor', 'Engine'),
                          ('engine', 'Engine'), ('replace', 'Engine')})
        self.assertEqual(len(entity_named(graph, 'replace')
                             .relations['instantiates']), 1)

    def test_qualified_type_resolves_to_its_last_name(self):
        graph = build('''
        class Outer {
            static class Inner {}
        }

        class User {
            private Outer.Inner inner = new Outer.Inner();
        }
        ''')

        self.assertEqual(related(graph, 'isOfType'), {('inner', 'Inner')})
        self.assertEqual(related(graph, 'instantiates'),
                         {('inner', 'Inner')})

    def test_method_without_a_body_builds_graph(self):
        graph = build('''
        class Native {
            static { int loaded = 1; }

            native void call();
        }
        ''')

        self.assertEqual(described(graph), {('class', 'Native'),
                                            ('method', 'call')})


OBSERVERS = '''
import java.util.*;

interface Observer {
    void update(String key);
}

class Logger implements Observer {
    public void update(String key) {}
}

class Subject {
    private List<Observer> observers = new ArrayList<>();
    private Observer[] watchers;
    private Map<String, List<Observer>> byTopic;
    private Optional<Observer> main;
    private List<String> names;

    void attach(Observer observer) { observers.add(observer); }

    void notifyObservers() {
        for (Observer observer : observers) {
            observer.update("key");
        }
    }

    void notifyFirst() { observers.get(0).update("key"); }

    void notifyWatcher() { watchers[0].update("key"); }

    void notifyOthers(List<Observer> others) {
        for (var other : others) {
            other.update("key");
        }
    }

    List<Observer> all() { return observers; }
}
'''


class TestCollections(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = build(OBSERVERS)

    def test_field_is_a_collection_of_its_type_arguments(self):
        # Whether a list, an array, or nested within another collection
        self.assertEqual(related(self.graph, 'isCollectionOf'),
                         {('observers', 'Observer'),
                          ('watchers', 'Observer'),
                          ('byTopic', 'Observer')})

    def test_optional_holds_a_single_value(self):
        self.assertEqual(related(self.graph, 'isOfType'),
                         {('main', 'Observer')})

    def test_type_arguments_of_parameters_and_return_types(self):
        self.assertEqual(related(self.graph, 'parameterOfType'),
                         {('attach', 'Observer'),
                          ('notifyOthers', 'Observer')})
        self.assertEqual(related(self.graph, 'hasReturnType'),
                         {('all', 'Observer')})

    def test_method_invoked_on_an_element_of_a_collection(self):
        # Adding to the list is not a method of any class in the project
        self.assertEqual(related_members(self.graph, 'invokes'),
                         {('Subject.notifyObservers', 'Observer.update'),
                          ('Subject.notifyFirst', 'Observer.update'),
                          ('Subject.notifyWatcher', 'Observer.update'),
                          ('Subject.notifyOthers', 'Observer.update')})


class TestInvokes(unittest.TestCase):
    def test_method_is_found_from_the_type_it_is_called_on(self):
        graph = build('''
        interface Engine {
            void start();
        }

        class Petrol implements Engine {
            public void start() {}
            void refuel() {}
        }

        class Diesel implements Engine {
            public void start() {}
        }

        class Car {
            private Engine engine;
            private Petrol spare = new Petrol();

            void drive() { engine.start(); }

            void service() {
                this.spare.refuel();
                check();
            }

            void check() {}

            void swap(Diesel diesel) { diesel.start(); }

            Engine engine() { return engine; }

            void restart() {
                engine().start();
                new Petrol().start();
            }

            void log() {
                System.out.println("log");
                String.valueOf(1).start();
            }
        }
        ''')

        self.assertEqual(related_members(graph, 'invokes'),
                         {('Car.drive', 'Engine.start'),
                          ('Car.service', 'Petrol.refuel'),
                          ('Car.service', 'Car.check'),
                          ('Car.swap', 'Diesel.start'),
                          ('Car.restart', 'Car.engine'),
                          ('Car.restart', 'Engine.start'),
                          ('Car.restart', 'Petrol.start')})

    def test_inherited_method_and_field_are_found(self):
        graph = build('''
        class Tool {
            void use() {}
        }

        class Base {
            protected Tool tool;

            void prepare() {}
        }

        class Worker extends Base {
            void work() {
                prepare();
                tool.use();
                super.prepare();
            }
        }
        ''')

        self.assertEqual(related_members(graph, 'invokes'),
                         {('Worker.work', 'Base.prepare'),
                          ('Worker.work', 'Tool.use')})

    def test_unknown_receiver_falls_back_to_the_only_method_of_that_name(
            self):
        graph = build('''
        import java.util.List;

        class Printer {
            void print() {}
            void flush() {}
        }

        class Spooler {
            void flush() {}
        }

        class Report {
            void run(List<String> items) {
                items.forEach(item -> item.print());
                items.forEach(item -> item.flush());
            }
        }
        ''')

        self.assertEqual(related_members(graph, 'invokes'),
                         {('Report.run', 'Printer.print')})


class TestOverrides(unittest.TestCase):
    def test_method_overrides_through_the_whole_hierarchy(self):
        graph = build('''
        interface Shape {
            double area();
            default String name() { return "shape"; }
        }

        abstract class Base implements Shape {}

        class Square extends Base {
            public double area() { return 1; }
            public String name() { return "square"; }
            public double area(int scale) { return scale; }
        }

        class Big extends Square {
            public double area() { return 2; }
        }
        ''')

        overrides = [relation for relation in graph['relations']
                     if relation.relation_type == 'overrides']

        self.assertEqual(related_members(graph, 'overrides'),
                         {('Square.area', 'Shape.area'),
                          ('Square.name', 'Shape.name'),
                          ('Big.area', 'Square.area'),
                          ('Big.area', 'Shape.area')})
        # A method with a different number of parameters is an overload
        self.assertEqual(len(overrides), 4)

    def test_static_and_private_methods_are_not_overridden(self):
        graph = build('''
        class Base {
            static void make() {}
            private void hide() {}
        }

        class Child extends Base {
            static void make() {}
            void hide() {}
        }
        ''')

        self.assertEqual(related(graph, 'overrides'), set())


class TestAssignsAndReturns(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = build('''
        class Account {
            private int balance;
            private Account parent;

            Account(int balance) { this.balance = balance; }

            void reset() {
                int local = 1;
                local = 2;
                balance = 0;
            }

            int balance() { return balance; }

            Account parent() { return this.parent; }

            int doubled() { return balance * 2; }
        }
        ''')

    def test_member_assigns_the_fields_it_sets(self):
        self.assertEqual(related(self.graph, 'assigns'),
                         {('Account Constructor', 'balance'),
                          ('reset', 'balance')})

    def test_method_returns_the_field_it_gives_back(self):
        self.assertEqual(related(self.graph, 'returns'),
                         {('balance', 'balance'), ('parent', 'parent')})


class TestLambdas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = build('''
        interface Strategy {
            int apply(int x);
        }

        class Maths {
            static int twice(int x) { return x * 2; }
        }

        class Context {
            private Strategy strategy = x -> Maths.twice(x);

            void set(Strategy strategy) { this.strategy = strategy; }

            void configure() { set(Maths::twice); }

            Strategy identity() { return x -> x; }

            void background() {
                Runnable task = () -> Maths.twice(1);
            }
        }
        ''')

    def test_lambda_is_a_class_implementing_the_interface_expected(self):
        lambdas = [entity for entity in self.graph['entities']
                   if entity.info['name'] == 'Lambda Strategy']

        # One assigned to a field, one passed to a method and one returned
        self.assertEqual(len(lambdas), 3)
        self.assertEqual(related(self.graph, 'implements'),
                         {('Lambda Strategy', 'Strategy')})
        self.assertEqual(related(self.graph, 'overrides'),
                         {('apply', 'apply')})
        self.assertEqual(related_members(self.graph, 'instantiates'),
                         {('Context.strategy', 'Lambda Strategy'),
                          ('Context.configure', 'Lambda Strategy'),
                          ('Context.identity', 'Lambda Strategy')})

    def test_code_in_lambda_belongs_to_the_method_it_implements(self):
        # Without an interface in the project to implement, the code
        # belongs to the method that the lambda is written in
        self.assertEqual(related_members(self.graph, 'invokes'),
                         {('Lambda Strategy.apply', 'Maths.twice'),
                          ('Context.configure', 'Context.set'),
                          ('Context.background', 'Maths.twice')})


class TestNameLookup(unittest.TestCase):
    def test_shared_name_is_found_by_import_then_by_package(self):
        graph = build(
            'package alpha; public class Token {}',
            'package beta; public class Token {}',
            'package gamma; import beta.Token; class Importer { Token t; }',
            'package alpha; class Neighbour { Token t; }',
            'package delta; class Stranger { Token t; }')

        packages = {relation.entity_from.package: relation.entity_to.package
                    for relation in graph['relations']
                    if relation.relation_type == 'isOfType'}

        # Neither Token is visible from a package that does not import one
        self.assertEqual(packages, {'gamma': 'beta', 'alpha': 'alpha'})

    def test_class_is_found_despite_a_member_sharing_its_name(self):
        graph = build('''
        class Order {}

        class Shop {
            private Order Order;
            Order latest() { return Order; }
        }
        ''')

        self.assertEqual(related(graph, 'hasReturnType'),
                         {('latest', 'Order')})


class TestModernSyntax(unittest.TestCase):
    def test_record_is_a_class_with_a_field_for_each_component(self):
        graph = build('''
        interface Shape {
            double area();
        }

        record Square(double side, Shape inner) implements Shape {
            public double area() { return side * side; }
        }
        ''')

        self.assertLessEqual({('class', 'Square'), ('field', 'side'),
                              ('field', 'inner'), ('method', 'area')},
                             described(graph))
        self.assertEqual(entity_named(graph, 'side').info['modifiers'],
                         {'private', 'final'})
        self.assertEqual(related(graph, 'implements'),
                         {('Square', 'Shape')})
        self.assertEqual(related(graph, 'isOfType'), {('inner', 'Shape')})

    def test_variable_bound_by_a_pattern_has_its_type(self):
        graph = build('''
        class Circle {
            double radius() { return 1; }
        }

        class Square {
            double side() { return 1; }
        }

        class Measure {
            double viaInstanceof(Object shape) {
                if (shape instanceof Circle circle) {
                    return circle.radius();
                }
                return 0;
            }

            double viaSwitch(Object shape) {
                return switch (shape) {
                    case Square square -> square.side();
                    default -> 0;
                };
            }
        }
        ''')

        self.assertEqual(related_members(graph, 'invokes'),
                         {('Measure.viaInstanceof', 'Circle.radius'),
                          ('Measure.viaSwitch', 'Square.side')})

    def test_annotated_types_are_resolved(self):
        graph = build('''
        import java.util.List;

        class Observer {}

        class Subject<T extends @Nullable Object> {
            private List<@NonNull Observer> observers;
            private @Nullable Observer main;
            private Observer @Nullable [] spare;

            Observer[] copy() { return create(Observer[]::new); }

            Observer[] create(Object maker) { return null; }
        }
        ''')

        self.assertEqual(related(graph, 'isCollectionOf'),
                         {('observers', 'Observer'), ('spare', 'Observer')})
        self.assertEqual(related(graph, 'isOfType'), {('main', 'Observer')})
        self.assertEqual(related(graph, 'invokes'), {('copy', 'create')})

    def test_method_invoked_on_a_cast_or_a_var(self):
        graph = build('''
        interface Engine {}

        class Petrol implements Engine {
            void refuel() {}
        }

        class Car {
            void viaCast(Engine engine) { ((Petrol) engine).refuel(); }

            void viaVar() {
                var engine = new Petrol();
                engine.refuel();
            }
        }
        ''')

        self.assertEqual(related_members(graph, 'invokes'),
                         {('Car.viaCast', 'Petrol.refuel'),
                          ('Car.viaVar', 'Petrol.refuel')})

    def test_file_with_a_syntax_error_is_parsed_as_far_as_it_can_be(self):
        graph = build('''
        class Broken {
            void first() {}

            void second( { }

            void third() { first(); }
        }

        class Whole {
            void run() {}
        }
        ''')

        self.assertLessEqual({('class', 'Broken'), ('method', 'first'),
                              ('method', 'third'), ('class', 'Whole'),
                              ('method', 'run')}, described(graph))
        self.assertIn(('third', 'first'), related(graph, 'invokes'))


if __name__ == '__main__':
    unittest.main()
