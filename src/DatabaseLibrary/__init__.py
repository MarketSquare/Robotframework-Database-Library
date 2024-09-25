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

import os

from DatabaseLibrary.assertion import Assertion
from DatabaseLibrary.connection_manager import ConnectionManager
from DatabaseLibrary.query import Query
from DatabaseLibrary.version import VERSION

__version__ = VERSION


class DatabaseLibrary(ConnectionManager, Query, Assertion):
    """
    The Database Library for [https://robotframework.org|Robot Framework] allows you to query a database and verify the results.
    It requires an appropriate *Python module to be installed separately* - depending on your database, like e.g. `oracledb` or `pymysql`.

    == Table of contents ==
    %TOC%

    = Requirements =
    - Python
    - Robot Framework
    - Python database module you're going to use - e.g. `oracledb`

    = Installation =
    | pip install robotframework-databaselibrary
    Don't forget to install the required Python database module!

    = Usage example =
    == Basic usage ==
    | *** Settings ***
    | Library       DatabaseLibrary
    | Test Setup    Connect To My Oracle DB
    |
    | *** Keywords ***
    | Connect To My Oracle DB
    |     Connect To Database
    |     ...    oracledb
    |     ...    dbName=db
    |     ...    dbUsername=my_user
    |     ...    dbPassword=my_pass
    |     ...    dbHost=127.0.0.1
    |     ...    dbPort=1521
    |
    | *** Test Cases ***
    | Person Table Contains Expected Records
    |     ${output}=    Query    select LAST_NAME from person
    |     Length Should Be    ${output}    2
    |     Should Be Equal    ${output}[0][0]    See
    |     Should Be Equal    ${output}[1][0]    Schneider
    |
    | Person Table Contains No Joe
    |     ${sql}=    Catenate    SELECT id FROM person
    |     ...                    WHERE FIRST_NAME= 'Joe'
    |     Check If Not Exists In Database    ${sql}
    |

    == Handling multiple database connections ==
    | *** Settings ***
    | Library          DatabaseLibrary
    | Test Setup       Connect To All Databases
    | Test Teardown    Disconnect From All Databases
    |
    | *** Keywords ***
    | Connect To All Databases
    |     Connect To Database    psycopg2    db    db_user    pass    127.0.0.1    5432
    |     ...    alias=postgres
    |     Connect To Database    pymysql    db    db_user    pass    127.0.0.1    3306
    |     ...    alias=mysql
    |
    | *** Test Cases ***
    | Using Aliases
    |     ${names}=    Query    select LAST_NAME from person    alias=postgres
    |     Execute Sql String    drop table XYZ                  alias=mysql
    |
    | Switching Default Alias
    |     Switch Database    postgres
    |     ${names}=    Query    select LAST_NAME from person
    |     Switch Database    mysql
    |     Execute Sql String    drop table XYZ
    |

    = Using configuration file =
    The `Connect To Database` keyword allows providing the connection parameters in two ways:
    - As keyword arguments
    - In a configuration file - a simple list of _key=value_ pairs, set inside an _alias_ section.

    You can use only one way or you can combine them:
    - The keyword arguments are taken by default
    - If no keyword argument is provided, a parameter value is searched in the config file

    Along with commonly used connection parameters, named exactly as keyword arguments, a config file
    can contain any other DB module specific parameters as key/value pairs.
    If same custom parameter is provided both as a keyword argument *and* in config file,
    the *keyword argument value takes precedence*.

    The path to the config file is set by default to `./resources/db.cfg`.
    You can change it using an according parameter in the `Connect To Database` keyword.

    A config file *must* contain at least one section name -
    the connection alias, if used (see `Handling multiple database connections`), or
    `[default]` if no aliases are used.

    == Config file examples ==
    === Config file with default alias (equal to using no aliases at all) ===
    | [default]
    | dbapiModuleName=psycopg2
    | dbName=yourdbname
    | dbUsername=yourusername
    | dbPassword=yourpassword
    | dbHost=yourhost
    | dbPort=yourport

    === Config file with a specific alias ===
    | [myoracle]
    | dbapiModuleName=oracledb
    | dbName=yourdbname
    | dbUsername=yourusername
    | dbPassword=yourpassword
    | dbHost=yourhost
    | dbPort=yourport

    === Config file with some params only ===
    | [default]
    | dbPassword=mysecret

    === Config file with some custom DB module specific params ===
    | [default]
    | my_custom_param=value


    = Inline assertions =
    Keywords, that accept arguments ``assertion_operator`` <`AssertionOperator`> and ``expected_value``,
    perform a check according to the specified condition - using the [https://github.com/MarketSquare/AssertionEngine|Assertion Engine].

    Examples:
    | Check Row Count | SELECT id FROM person | *==* | 2 |
    | Check Query Result | SELECT first_name FROM person | *contains* | Allan |

    = Retry mechanism =
    Assertion keywords, that accept arguments ``retry_timeout`` and ``retry_pause``, support waiting for assertion to pass.

    Setting the ``retry_timeout`` argument enables the mechanism -
    in this case the SQL request and the assertion are executed in a loop,
    until the assertion is passed or the ``retry_timeout`` is reached.
    The pause between the loop iterations is set using the ``retry_pause`` argument.

    The argument values are set in [http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#time-format|Robot Framework time format] -
    e.g. ``5 seconds``.

    The retry mechanism is disabled by default - the ``retry_timeout`` is set to ``0``.

    Examples:
    | Check Row Count | SELECT id FROM person | *==* | 2 | retry_timeout=10 seconds |
    | Check Query Result | SELECT first_name FROM person | *contains* | Allan | retry_timeout=5s | retry_timeout=1s |

    = Logging query results =
    Keywords, that fetch results of a SQL query, print the result rows as a table in RF log.
    - A log head limit of *50 rows* is applied, other table rows are truncated in the log message.
    - The limit and the logging in general can be adjusted any time in your tests using the Keyword `Set Logging Query Results`.

    You can also setup the limit or disable the logging during the library import.
    Examples:

    | # Default behavior - logging of query results is enabled, log head is 50 rows.
    | *** Settings ***
    | Library    DatabaseLibrary
    |
    | # Logging of query results is disabled, log head is 50 rows (default).
    | Library    DatabaseLibrary    log_query_results=False
    |
    | # Logging of query results is enabled (default), log head is 10 rows.
    | Library    DatabaseLibrary    log_query_results_head=10
    |
    | # Logging of query results is enabled (default), log head limit is disabled (log all rows).
    | Library    DatabaseLibrary    log_query_results_head=0

    = Database modules compatibility =
    The library is basically compatible with any [https://peps.python.org/pep-0249|Python Database API Specification 2.0] module.

    However, the actual implementation in existing Python modules is sometimes quite different, which requires custom handling in the library.
    Therefore, there are some modules, which are "natively" supported in the library - and others, which may work and may not.

    See more on the [https://github.com/MarketSquare/Robotframework-Database-Library|project page on GitHub].
    """

    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self, log_query_results=True, log_query_results_head=50):
        """
        The library can be imported without any arguments:
        | *** Settings ***
        | Library    DatabaseLibrary
        Use optional library import parameters to disable `Logging query results` or setup the log head.
        """
        ConnectionManager.__init__(self)
        if log_query_results_head < 0:
            raise ValueError(f"Wrong log head value provided: {log_query_results_head}. The value can't be negative!")
        Query.__init__(self, log_query_results=log_query_results, log_query_results_head=log_query_results_head)
