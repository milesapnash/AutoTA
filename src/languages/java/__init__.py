from src.languages.java.filter import JavaFilter
from src.languages.java.graph import build_java_graph
from src.languages.java.parser import parse_java
from src.languages.language import Language

JAVA = Language('.java', parse_java, JavaFilter, build_java_graph)
