from collections import namedtuple

Language = namedtuple('Language',
                      ['extension', 'parse', 'filter', 'build_graph'])
