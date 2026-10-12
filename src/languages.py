import ast
from collections import namedtuple

import tree_sitter_java
from tree_sitter import Language as Grammar, Parser

from src.filters.java_filter import JavaFilter
from src.filters.python_filter import PythonFilter
from src.graph.java_graph import build_java_graph
from src.graph.python_graph import build_python_graph

Language = namedtuple('Language',
                      ['extension', 'parse', 'filter', 'build_graph'])


JAVA_GRAMMAR = Grammar(tree_sitter_java.language())


def parse_java(contents):
    # A file with syntax errors is still parsed, as far as it can be
    return Parser(JAVA_GRAMMAR).parse(contents.encode('utf-8')).root_node


# To support another language, register its file extension, parser, filter
# and ER graph builder here
LANGUAGES = {
    'java': Language('.java', parse_java, JavaFilter, build_java_graph),
    'python': Language('.py', ast.parse, PythonFilter, build_python_graph)
}


def language_of(file_name):
    for name, language in LANGUAGES.items():
        if file_name.endswith(language.extension):
            return name
    return None
