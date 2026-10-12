import tree_sitter_java
from tree_sitter import Language as Grammar, Parser

JAVA_GRAMMAR = Grammar(tree_sitter_java.language())


def parse_java(contents):
    # A file with syntax errors is still parsed, as far as it can be
    return Parser(JAVA_GRAMMAR).parse(contents.encode('utf-8')).root_node
