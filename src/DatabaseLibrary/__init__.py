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

    = Basic usage examples =
    | *** Settings ***
    | Library       DatabaseLibrary
    | Test Setup    Connect To My Oracle DB
    |
    | *** Keywords ***
    | Connect To My Oracle DB
    |     Connect To Database
    |     ...    oracledb
    |     ...    db_name=db
    |     ...    db_user=my_user
    |     ...    db_password=my_pass
    |     ...    db_host=127.0.0.1
    |     ...    db_port=1521
    |
    | *** Test Cases ***
    | Get All Names
    |     ${Rows}=    Query    select FIRST_NAME, LAST_NAME from person
    |     Should Be Equal    ${Rows}[0][0]    Franz Allan
    |     Should Be Equal    ${Rows}[0][1]    See
    |     Should Be Equal    ${Rows}[1][0]    Jerry
    |     Should Be Equal    ${Rows}[1][1]    Schneider
    |
    | Person Table Contains Expected Records
    |     ${sql}=    Catenate    select LAST_NAME from person
    |     Check Query Result    ${sql}    contains    See
    |     Check Query Result    ${sql}    equals      Schneider    row=1
    |
    | Wait Until Table Gets New Record
    |     ${sql}=    Catenate    select LAST_NAME from person
    |     Check Row Count    ${sql}    >    2    retry_timeout=5s
    |
    | Person Table Contains No Joe
    |     ${sql}=    Catenate    SELECT id FROM person
    |     ...                    WHERE FIRST_NAME= 'Joe'
    |     Check Row Count    ${sql}   ==    0
    |

    = Handling multiple database connections =
    The library can handle multiple connections to different databases using *aliases*.
    An alias is set while creating a connection and can be passed to library keywords in a corresponding argument.
    == Example ==
    | *** Settings ***
    | Library          DatabaseLibrary
    | Test Setup       Connect To All Databases
    | Test Teardown    Disconnect From All Databases
    |
    | *** Keywords ***
    | Connect To All Databases
    |     Connect To Database
    |     ...    psycopg2
    |     ...    db_name=db
    |     ...    db_user=db_user
    |     ...    db_password=pass
    |     ...    db_host=127.0.0.1
    |     ...    db_port=5432
    |     ...    alias=postgres
    |     Connect To Database
    |     ...    pymysql
    |     ...    db_name=db
    |     ...    db_user=db_user
    |     ...    db_password=pass
    |     ...    db_host=127.0.0.1
    |     ...    db_port=3306
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

    = Connection examples for different DB modules =
    == Oracle (oracle_db) ==
    | # Thin mode is used by default
    | Connect To Database
    | ...    oracledb
    | ...    db_name=db
    | ...    db_user=db_user
    | ...    db_password=pass
    | ...    db_host=127.0.0.1
    | ...    db_port=1521
    |
    | # Thick mode with default location of the Oracle Instant Client
    | Connect To Database
    | ...    oracledb
    | ...    db_name=db
    | ...    db_user=db_user
    | ...    db_password=pass
    | ...    db_host=127.0.0.1
    | ...    db_port=1521
    | ...    oracle_driver_mode=thick
    |
    | # Thick mode with custom location of the Oracle Instant Client
    | Connect To Database
    | ...    oracledb
    | ...    db_name=db
    | ...    db_user=db_user
    | ...    db_password=pass
    | ...    db_host=127.0.0.1
    | ...    db_port=1521
    | ...    oracle_driver_mode=thick,lib_dir=C:/instant_client_23_5
    == PostgreSQL (psycopg2) ==
    | Connect To Database
    | ...    psycopg2
    | ...    db_name=db
    | ...    db_user=db_user
    | ...    db_password=pass
    | ...    db_host=127.0.0.1
    | ...    db_port=5432
    == Microsoft SQL Server (pymssql) ==
    | # UTF-8 charset is used by default
    | Connect To Database
    | ...    pymssql
    | ...    db_name=db
    | ...    db_user=db_user
    | ...    db_password=pass
    | ...    db_host=127.0.0.1
    | ...    db_port=1433
    |
    | # Specifying a custom charset
    | Connect To Database
    | ...    pymssql
    | ...    db_name=db
    | ...    db_user=db_user
    | ...    db_password=pass
    | ...    db_host=127.0.0.1
    | ...    db_port=1433
    | ...    db_charset=cp1252
    == MySQL (pymysql) ==
    | # UTF-8 charset is used by default
    | Connect To Database
    | ...    pymysql
    | ...    db_name=db
    | ...    db_user=db_user
    | ...    db_password=pass
    | ...    db_host=127.0.0.1
    | ...    db_port=3306
    |
    | # Specifying a custom charset
    | Connect To Database
    | ...    pymysql
    | ...    db_name=db
    | ...    db_user=db_user
    | ...    db_password=pass
    | ...    db_host=127.0.0.1
    | ...    db_port=3306
    | ...    db_charset=cp1252
    == IBM DB2 (ibm_db) ==
    | Connect To Database
    | ...    ibm_db_dbi
    | ...    db_name=db
    | ...    db_user=db_user
    | ...    db_password=pass
    | ...    db_host=127.0.0.1
    | ...    db_port=50000
    == MySQL via ODBC (pyodbc) ==
    | # ODBC driver name is required
    | # ODBC driver itself has to be installed
    | Connect To Database
    | ...    pyodbc
    | ...    db_name=db
    | ...    db_user=db_user
    | ...    db_password=pass
    | ...    db_host=127.0.0.1
    | ...    db_port=3306
    | ...    odbc_driver={MySQL ODBC 9.2 ANSI Driver}
    |
    | # Specifying a custom charset if needed
    | Connect To Database
    | ...    pyodbc
    | ...    db_name=db
    | ...    db_user=db_user
    | ...    db_password=pass
    | ...    db_host=127.0.0.1
    | ...    db_port=3306
    | ...    odbc_driver={MySQL ODBC 9.2 ANSI Driver}
    | ...    db_charset=latin1
    == Oracle via JDBC (jaydebeapi) ==
    | # Username and password must be set as a dictionary
    | VAR  &{CREDENTIALS}  user=db_user  password=pass
    |
    | # JAR file with Oracle JDBC driver is required
    | # Jaydebeapi is not "natively" supported by the Database Library,
    | # so using the custom parameters
    | Connect To Database
    | ...    jaydebeapi
    | ...    jclassname=oracle.jdbc.driver.OracleDriver
    | ...    url=jdbc:oracle:thin:@127.0.0.1:1521/db
    | ...    driver_args=${CREDENTIALS}
    | ...    jars=C:/ojdbc17.jar
    |
    | # Set if getting error 'Could not commit/rollback with auto-commit enabled'
    | Set Auto Commit    False
    |
    | # Set for automatically removing trailing ';' (might be helpful for Oracle)
    | Set Omit Trailing Semicolon    True
    ==  SQLite (sqlite3) ==
    | # Using custom parameters required
    | Connect To Database
    | ...    sqlite3
    | ...    database=./my_database.db
    | ...    isolation_level=${None}
    == Teradata (teradata) ==
    | Connect To Database
    | ...    teradata
    | ...    db_name=db
    | ...    db_user=db_user
    | ...    db_password=pass
    | ...    db_host=127.0.0.1
    | ...    db_port=1025

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
    | db_module=psycopg2
    | db_name=yourdbname
    | db_user=yourusername
    | db_password=yourpassword
    | db_host=yourhost
    | db_port=yourport

    === Config file with a specific alias ===
    | [myoracle]
    | db_module=oracledb
    | db_name=yourdbname
    | db_user=yourusername
    | db_password=yourpassword
    | db_host=yourhost
    | db_port=yourport

    === Config file with some params only ===
    | [default]
    | db_password=mysecret

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

    The retry mechanism is disabled by default - ``retry_timeout`` is set to ``0``.

    Examples:
    | Check Row Count | SELECT id FROM person | *==* | 2 | retry_timeout=10 seconds |
    | Check Query Result | SELECT first_name FROM person | *contains* | Allan | retry_timeout=5s | retry_pause=1s |

    = Logging query results =
    Keywords, that fetch results of a SQL query, print the result rows as a table in RF log.
    - A log head limit of *50 rows* is applied, other table rows are truncated in the log message.
    - The limit and the logging in general can be adjusted any time in your tests using the Keyword `Set Logging Query Results`.

    You can also setup the limit or disable the logging during the library import.
    Examples:

    | *** Settings ***
    | # Default behavior - logging of query results is enabled, log head is 50 rows.
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

    = Commit behavior =
    While creating a database connection, the library doesn't explicitly set the _autocommit_ behavior -
    so the default value of the Python DB module is used.
    According to Python DB API specification it should be disabled by default -
    which means each SQL transaction (even a simple _SELECT_) must contain a dedicated commit statement, if necessary.

    The library manages it for you - keywords like `Query` or `Execute SQL String`
    perform automatically a commit after running the query (or a rollback in case of error).

    You can turn off this automatic commit/rollback behavior using the ``no_transaction`` parameter.
    See docs of a particular keyword.

    It's also possible to explicitly set the _autocommit_ behavior on the Python DB module level -
    using the `Set Auto Commit` keyword.
    This has no impact on the automatic commit/rollback behavior in library keywords (described above).

    = Omitting trailing semicolon behavior =
    Some databases (e.g. Oracle) throw an exception, if you leave a semicolon (;) at the SQL string end.
    However, there are exceptional cases, when you need it even for Oracle - e.g. at the end of a PL/SQL block.

    The library can handle it for you and remove the semicolon at the end of the SQL string.
    By default, it's decided based on the current database module in use:
    - For `oracle_db` and `cx_Oracle`, the trailing semicolon is removed
    - For other modules, the trailing semicolon is left as it is

    You can also set this behavior explicitly:
    - Using the `Set Omit Trailing Semicolon` keyword
    - Using the `omit_trailing_semicolon` parameter in the `Execute SQL String` keyword.

    = Database modules compatibility =
    The library is basically compatible with any [https://peps.python.org/pep-0249|Python Database API Specification 2.0] module.

    However, the actual implementation in existing Python modules is sometimes quite different, which requires custom handling in the library.
    Therefore, there are some modules, which are "natively" supported in the library - and others, which may work and may not.

    == Python modules currently "natively" supported ==
    === Oracle ===
    [https://oracle.github.io/python-oracledb/|oracledb]
    - Both thick and thin client modes are supported - you can select one using the `oracle_driver_mode` parameter.
    - However, due to current limitations of the oracledb module, *it's not possible to switch between thick and thin modes during a test execution session* - even in different suites.

    [https://oracle.github.io/python-cx_Oracle/|cx_Oracle]

    === MySQL ===
    - [https://github.com/PyMySQL/PyMySQL|pymysql]
    - [https://mysqlclient.readthedocs.io/index.html|MySQLdb]
    === PostgreSQL ===
    - [https://www.psycopg.org/docs/|psycopg2]
    === MS SQL Server ===
    - [https://github.com/pymssql/pymssql|pymssql]
    === SQLite ===
    - [https://docs.python.org/3/library/sqlite3.html|sqlite3]
    === Teradata ===
    - [https://github.com/teradata/PyTd|teradata]
    === IBM DB2 ===
    - The Python package to be installed is [https://github.com/ibmdb/python-ibmdb|ibm_db]. It includes two modules - `ibm_db` and `ibm_db_dbi`.
    - Using *`ibm_db_dbi` is highly recommended* as only this module is Python DB API 2.0 compatible. See [https://www.ibm.com/docs/en/db2/12.1?topic=applications-python-sqlalchemy-django-framework|official docs].
    === ODBC ===
    - [https://github.com/mkleehammer/pyodbc|pyodbc]
    - [https://github.com/pypyodbc/pypyodbc|pypyodbc]
    === Kingbase ===
    - ksycopg2
    """

    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LIBRARY_VERSION = __version__

    def __init__(self, log_query_results=True, log_query_results_head=50, warn_on_connection_overwrite=True):
        """
        The library can be imported without any arguments:
        | *** Settings ***
        | Library    DatabaseLibrary

        Use optional library import parameters:
        - ``log_query_results`` and ``log_query_results_head`` to disable `Logging query results` or setup the log head
        - ``warn_on_connection_overwrite`` to disable the warning about overwriting an existing connection
        """
        ConnectionManager.__init__(self, warn_on_connection_overwrite=warn_on_connection_overwrite)
        if log_query_results_head < 0:
            raise ValueError(f"Wrong log head value provided: {log_query_results_head}. The value can't be negative!")
        Query.__init__(self, log_query_results=log_query_results, log_query_results_head=log_query_results_head)
