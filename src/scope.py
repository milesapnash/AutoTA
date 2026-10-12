import os

# Directories that hold dependencies and caches rather than a project's code
IGNORED_DIRECTORIES = {'node_modules', '__pycache__', 'site-packages'}
# Directories that a build tool writes to, where the directory they are in
# holds one of the files that such a tool is configured by
BUILD_DIRECTORIES = {'target', 'build', 'out', 'dist'}
BUILD_FILES = {'pom.xml', 'build.gradle', 'build.gradle.kts',
               'settings.gradle', 'settings.gradle.kts', 'build.xml',
               'setup.py', 'pyproject.toml'}


def path_parts(path):
    """Returns the directories named in a path, so that both src/main and
    ./src\\main give src and main."""
    normalised = os.path.normpath(path or '.').replace('\\', '/')
    return [part for part in normalised.split('/') if part not in ('', '.')]


def in_scope(relative_dir, scope):
    """Checks whether a directory is within a scope, which is a directory
    given by its name, such as main, or by a path, such as src/main. The
    scope may be anywhere in the path to the directory, so that main covers
    src/main/java in a Maven project. Every directory is within the scope
    of the project directory itself, given as a dot."""
    scope_parts = path_parts(scope)
    directory_parts = path_parts(relative_dir)
    return any(
        directory_parts[start:start + len(scope_parts)] == scope_parts
        for start in range(len(directory_parts) - len(scope_parts) + 1))


def is_ignored(parent, name, sibling_files):
    """Checks whether a directory holds something other than the code of
    the project: it is hidden, a virtual environment, a dependency cache or
    the output of a build."""
    return (name.startswith('.')
            or name in IGNORED_DIRECTORIES
            or (name in BUILD_DIRECTORIES
                and not BUILD_FILES.isdisjoint(sibling_files))
            or os.path.exists(os.path.join(parent, name, 'pyvenv.cfg')))


def walk_source(directory):
    """Yields each directory of a project with the files in it, in a fixed
    order, leaving out the directories that do not hold its code."""
    for root, directories, files in os.walk(directory):
        directories[:] = sorted(name for name in directories
                                if not is_ignored(root, name, files))
        yield root, sorted(files)
