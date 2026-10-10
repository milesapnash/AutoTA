import argparse
import os

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
    parser.add_argument('spec', nargs='?', default='',
                        help='specification file (currently unused, the '
                             'specification is built in spec.py)')
    parser.add_argument('--scope', default='main',
                        help='subdirectory used to build the entity-relation '
                             'graph (default: main)')
    parser.add_argument('--pdf', action='store_true',
                        help='write the feedback to a PDF')
    parser.add_argument('--output', default='feedback.pdf',
                        help='path of the PDF written by --pdf (default: '
                             'feedback.pdf in the current directory)')
    return parser.parse_args()


def main():
    load_dotenv()
    args = parse_args()

    spec = build_spec(args.spec)
    print('-Specification Built Successfully')
    project = ReviewProject(args.directory, spec, er_scope=args.scope)
    print('-Project Built Successfully')
    project.print_feedback()

    if os.getenv('OPENAI_API_KEY'):
        project.get_llm_summary()

    if args.pdf:
        project.build_pdf(args.output)


if __name__ == '__main__':
    main()
