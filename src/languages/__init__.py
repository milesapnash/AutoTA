from src.languages.java import JAVA
from src.languages.python import PYTHON

# To support another language, add a package for it here that gives its
# Language, as java and python do, and register it
LANGUAGES = {
    'java': JAVA,
    'python': PYTHON,
}


def language_of(file_name):
    for name, language in LANGUAGES.items():
        if file_name.endswith(language.extension):
            return name
    return None
