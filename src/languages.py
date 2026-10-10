import ast
from collections import namedtuple

import javalang

from src.entity_relations.java_graph import build_java_graph
from src.filters.java_filter import JavaFilter
from src.filters.python_filter import PythonFilter

Language = namedtuple('Language',
                      ['extension', 'parse', 'filter', 'build_graph'])


def parse_java(contents):
    tokens = list(javalang.tokenizer.tokenize(contents))
    return javalang.parser.Parser(tokens).parse()


# To support another language, register its file extension, parser, filter
# and ER graph builder here
LANGUAGES = {
    'java': Language('.java', parse_java, JavaFilter, build_java_graph),
    'python': Language('.py', ast.parse, PythonFilter, None)
}


def language_of(file_name):
    for name, language in LANGUAGES.items():
        if file_name.endswith(language.extension):
            return name
    return None
