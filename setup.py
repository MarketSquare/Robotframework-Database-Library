#!/usr/bin/env python

#  Copyright (c) 2010 Franz Allan Valencia See
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


"""Setup script for Robot's SQLAlchemyLibrary distributions"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sys, os
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

__version_file_path__ = os.path.join(src_path, 'SQLAlchemyLibrary', 'VERSION')
__version__ = open(__version_file_path__, 'r').read().strip()

def main():
    setup(name         = 'robotframework-SQLAlchemyLibrary',
          version      = __version__,
          description  = 'SQLAlchemy wrapper library for Robot Framework; forked from robotframework-database-library 0.6',
          author       = 'Ed Brannin',
          author_email = 'edbrannin@gmail.com',
          url          = 'https://github.com/edbrannin/Robotframework-SQLAlchemy-Library',
          package_dir  = { '' : 'src'},
          install_requires = ['robotframework'],
          packages     = ['SQLAlchemyLibrary'],
          )
        

if __name__ == "__main__":
    main()
