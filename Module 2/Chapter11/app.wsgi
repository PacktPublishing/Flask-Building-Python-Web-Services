activate_this = '/Users/shalabhaggarwal/workspace/mydev/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from my_app import app as application
import sys, logging
logging.basicConfig(stream = sys.stderr)
