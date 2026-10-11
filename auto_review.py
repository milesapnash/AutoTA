import argparse
import os
import sys

from dotenv import load_dotenv

from src.project.review_project import ReviewProject
from src.project.spec import build_spec


def parse_args():
    parser = argparse.ArgumentParser(
        description='Generate feedback on the structure of object-oriented '
                    'code.')
    parser.add_argument('directory', nargs='?',
                        default='test/example_task_java/',
                        help='project directory to review (default: the '
                             'bundled Java example task)')
    parser.add_argument('--scope', default='main',
                        help='directory used to build the entity-relation '
                             'graph, by name or path and wherever it is in '
                             'the project, or . for the whole project '
                             '(default: main)')
    parser.add_argument('--pdf', action='store_true',
                        help='write the feedback to a PDF')
    parser.add_argument('--output', default='feedback.pdf',
                        help='path of the PDF written by --pdf (default: '
                             'feedback.pdf in the current directory)')
    return parser.parse_args()


def main():
    load_dotenv()
    args = parse_args()

    spec = build_spec()
    print('-Specification Built Successfully')
    try:
        project = ReviewProject(args.directory, spec, er_scope=args.scope)
    except ValueError as error:
        sys.exit(f'-Project Could Not Be Built: {error}')
    print('-Project Built Successfully')
    project.print_feedback()

    if os.getenv('OPENAI_API_KEY'):
        project.get_llm_summary()

    if args.pdf:
        project.build_pdf(args.output)


if __name__ == '__main__':
    main()
