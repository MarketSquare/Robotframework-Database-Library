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


"""Setup script for Robot's DatabaseLibrary distributions"""

from distutils.core import setup

import setuptools
import sys
import os

src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

__version_file_path__ = os.path.join(src_path, 'DatabaseLibrary', 'VERSION')
__version__ = open(__version_file_path__, 'r').read().strip()

def main():
    setup(name         = 'robotframework-databaselibrary',
          version      = __version__,
          description  = 'Database utility library for Robot Framework',
          author       = 'Franz Allan Valencia See',
          author_email = 'franz.see@gmail.com',
          url          = 'https://github.com/franz-see/Robotframework-Database-Library',
          package_dir  = { '' : 'src'},
          packages     = ['DatabaseLibrary'],
          package_data = {'DatabaseLibrary': ['VERSION']},
          requires     = ['robotframework']
          )


if __name__ == "__main__":
    main()
