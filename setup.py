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

long_description = """
The Database Library for [Robot Framework](https://robotframework.org) allows you to query a database and verify the results.
It requires an appropriate **Python module to be installed separately** - depending on your database, like e.g. `oracledb` or `pymysql`. 

The library consists of some keywords designed to perform different checks on your database.
Here you can find the [keyword docs](http://marketsquare.github.io/Robotframework-Database-Library/).

# Requirements
- Python
- Robot Framework
- Python database module you're going to use - e.g. `oracledb`

# Installation
```
pip install robotframework-databaselibrary
```
Don't forget to install the required Python database module!

# Usage example
```RobotFramework
*** Settings ***
Library       DatabaseLibrary
Test Setup    Connect To My Oracle DB

*** Keywords ***
Connect To My Oracle DB
    Connect To Database
    ...    oracledb
    ...    dbName=db
    ...    dbUsername=my_user
    ...    dbPassword=my_pass
    ...    dbHost=127.0.0.1
    ...    dbPort=1521

*** Test Cases ***
Person Table Contains Expected Records
    ${output}=    Query    select LAST_NAME from person
    Length Should Be    ${output}    2
    Should Be Equal    ${output}[0][0]    See
    Should Be Equal    ${output}[1][0]    Schneider

Person Table Contains No Joe
    ${sql}=    Catenate    SELECT id FROM person
    ...                    WHERE FIRST_NAME= 'Joe'    
    Check If Not Exists In Database    ${sql}
```

# Database modules compatibility
The library is basically compatible with any [Python Database API Specification 2.0](https://peps.python.org/pep-0249/) module.

However, the actual implementation in existing Python modules is sometimes quite different, which requires custom handling in the library.
Therefore there are some modules, which are "natively" supported in the library - and others, which may work and may not.

See more on the [project page on GitHub](https://github.com/MarketSquare/Robotframework-Database-Library).
"""

version_file = join(dirname(abspath(__file__)), 'src', 'DatabaseLibrary', 'version.py')

with open(version_file) as file:
    code = compile(file.read(), version_file, 'exec')
    exec(code)

setup(name         = 'robotframework-databaselibrary',
      version      = VERSION,
      description  = 'Database utility library for Robot Framework',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author       = 'Franz Allan Valencia See',
      author_email = 'franz.see@gmail.com',
      url          = 'https://github.com/MarketSquare/Robotframework-Database-Library',
      package_dir  = { '' : 'src'},
      packages     = ['DatabaseLibrary'],
      package_data = {'DatabaseLibrary': []},
      requires     = ['robotframework']
      )
