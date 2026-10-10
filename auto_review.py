import os
import sys

from dotenv import load_dotenv

from src.project.review_project import ReviewProject
from src.project.spec import build_spec

if __name__ == "__main__":
    load_dotenv()

    repo_dir, spec_file = None, None
    if len(sys.argv) < 3:
        # Internal Testing
        repo_dir = 'test/example_task/'
        spec = build_spec("")
    else:
        # Command Line
        repo_dir = sys.argv[1]
        spec_file = sys.argv[2]

    spec = build_spec(spec_file)
    print('-Specification Built Successfully')
    project = ReviewProject(repo_dir, spec, er_scope='main')
    print('-Project Built Successfully')
    project.print_feedback()
    if os.getenv('OPENAI_API_KEY'):
        project.get_llm_summary()

    if False:
        project.build_pdf()
