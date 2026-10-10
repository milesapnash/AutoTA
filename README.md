# AutoTA
### Detecting Structural Patterns in Object-Oriented Code

AutoTA gives feedback on the structure of student code written in Java or Python. It parses a project into an entity-relation graph and looks for design patterns (Singleton, Template Method, Strategy) by matching subgraphs. It also checks rules such as encapsulation and naming conventions, and can ask an LLM to summarise the results.

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

With no arguments it reviews `test/example_task_java`; `test/example_task_python` is the same task in Python. The language is taken from the project's files. Feedback is printed, and `--pdf` also writes it to a PDF (`feedback.pdf` by default). `--scope` is the subdirectory the graph is built from (`main` by default).

The rules and patterns that are checked are set in `src/project/spec.py`.

In Python, a leading underscore is treated as private, and types are taken from annotations where they exist.

## Tests

```
python -m unittest discover -s test
```

## Building the report

`doc/report/build_report.sh` (or `.bat`) builds the report PDF. It needs `latexmk`, Pygments and Inkscape. With MiKTeX, enable automatic installation of missing packages first.
