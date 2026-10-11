# AutoTA
### Detecting Structural Patterns in Object-Oriented Code

AutoTA gives feedback on the structure of student code written in Java or Python. It parses a project into an entity-relation graph and looks for the 23 Gang of Four design patterns by matching subgraphs. It also checks rules such as encapsulation and naming conventions, and can ask an LLM to summarise the results.

Developed as part of my MEng Computing Individual Project at Imperial College London. The [report](doc/report.pdf) and [slides](doc/slides.pdf) are in `doc/`, and the version as submitted is the [v1.0 release](https://github.com/milesapnash/AutoTA/releases/tag/v1.0-meng-submission).

## Setup

Requires Python 3.12.

```
python -m venv .venv
.venv\Scripts\activate        # source .venv/bin/activate on Linux/macOS
pip install -r requirements.txt
```

To see the entity-relation graph while building it, also install `requirements-plot.txt`.

The LLM summary is optional. To use it, copy `.env.example` to `.env` and set `OPENAI_API_KEY`.

## Usage

```
python auto_review.py [directory] [--scope SCOPE] [--pdf] [--output PATH]
```

With no arguments it reviews `test/example_task_java`; `test/example_task_python` is the same task in Python. The language is taken from the project's files. Feedback is printed, and `--pdf` also writes it to a PDF (`feedback.pdf` by default). `--scope` is the directory the graph is built from (`main` by default). It is given by name or by path and may be anywhere in the project, so `main` covers `src/main/java` in a Maven project; `--scope .` uses the whole project.

Hidden directories, virtual environments, `node_modules` and the output of a build (such as `target` beside a `pom.xml`) are not reviewed.

The rules and patterns that are checked are set in `src/project/spec.py`.

Each pattern is defined in `src/entity_relations/design_pattern.py` as the classes, methods and fields it needs and the relations between them, such as which method invokes which. A definition can also give relations that must not hold: the context of a Strategy, for example, must not implement the strategy it holds. `test/pattern_repos` has a small example of every pattern in both languages. Patterns with a similar structure can be reported for the same code: a Command, for example, also has the shape of an Adapter.

In Python, a leading underscore is treated as private, and types are taken from annotations where they exist. Most patterns depend on types, so they are only found in annotated code.

Java is parsed with [tree-sitter](https://tree-sitter.github.io/tree-sitter/), which handles current Java syntax such as records and switch expressions. A file with a syntax error is still parsed as far as it can be, so one broken file does not stop a review. A Python file that cannot be parsed is listed in the feedback, and the rest of the project is reviewed without it.

The PDF is written with built-in fonts, so a character they lack, such as one in Chinese, appears as a question mark.

## Tests

```
python -m unittest discover -s test
```

## Building the report

`doc/report/build_report.sh` (or `.bat`) builds the report PDF. It needs `latexmk`, Pygments and Inkscape. With MiKTeX, enable automatic installation of missing packages first.

## Licence

The code is released under the [MIT licence](LICENSE). The report and slides in `doc/` are released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), except for the Imperial logo, which belongs to Imperial College London.
