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

from os.path import abspath, dirname, join

try:
    from setuptools import setup
except ImportError as error:
    from distutils.core import setup


version_file = join(dirname(abspath(__file__)), 'src', 'DatabaseLibrary', 'version.py')
pkg_vars  = {}

with open(version_file) as fp:
    exec(fp.read(), pkg_vars)

setup(name         = 'robotframework-databaselibrary',
      version      = pkg_vars['VERSION'],
      description  = 'Database utility library for Robot Framework',
      author       = 'Franz Allan Valencia See',
      author_email = 'franz.see@gmail.com',
      url          = 'https://github.com/franz-see/Robotframework-Database-Library',
      package_dir  = { '' : 'src'},
      packages     = ['DatabaseLibrary'],
      package_data = {'DatabaseLibrary': []},
      requires     = ['robotframework']
      )
