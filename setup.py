#!/usr/bin/env python

"""Setup script for Robot's DatabaseLibrary distributions"""

from distutils.core import setup

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from DatabaseLibrary import __version__

def main():
    setup(name         = 'robotframework-databaselibrary',
          version      = __version__,
          description  = 'Database utility library for Robot Framework',
          author       = 'Franz Allan Valencia See',
          author_email = 'franz.see@gmail.com',
          url          = 'http://code.google.com/p/franz.see/',
          package_dir  = { '' : 'src'},
          packages     = ['DatabaseLibrary']
          )
        

if __name__ == "__main__":
    main()
