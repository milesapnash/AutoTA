import ast

from src.languages.language import Language
from src.languages.python.filter import PythonFilter
from src.languages.python.graph import build_python_graph

PYTHON = Language('.py', ast.parse, PythonFilter, build_python_graph)
