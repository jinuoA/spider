"""
Usage:
  gerapy init [--folder=<folder>]
  gerapy migrate
  gerapy createsuperuser
  gerapy runserver
  gerapy makemigrations

Options:
  -h --help
  -v --version
"""
from docopt import docopt
#from spiderMonitor import version
from cmd.init import init
from cmd.server import server


def cmd():
    arguments = docopt(__doc__, version=version())
    
    if arguments.get('init'):
        init(arguments.get('--folder'))
    else:
        server(arguments.get('--port'), arguments.get('--host'))
