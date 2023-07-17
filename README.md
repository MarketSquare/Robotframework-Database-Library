# Robot Framework Database Library

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
See more examples in the folder `tests`.
# Database modules compatibility
The library is basically compatible with any [Python Database API Specification 2.0](https://peps.python.org/pep-0249/) module.

However, the actual implementation in existing Python modules is sometimes quite different, which requires custom handling in the library.
Therefore there are some modules, which are "natively" supported in the library - and others, which may work and may not.

## Python modules currently "natively" supported
### Oracle
- [oracledb](https://oracle.github.io/python-oracledb/)
- [cx_Oracle](https://oracle.github.io/python-cx_Oracle/)
### MySQL
- [pymysql](https://github.com/PyMySQL/PyMySQL)
- [MySQLdb](https://mysqlclient.readthedocs.io/index.html)
### PostgreSQL
- [psycopg2](https://www.psycopg.org/docs/)
### MS SQL Server
- [pymssql](https://github.com/pymssql/pymssql)
### SQLite
- [sqlite3](https://docs.python.org/3/library/sqlite3.html)
### Teradata
- [teradata](https://github.com/teradata/PyTd)
### IBM DB2
- [ibm_db](https://github.com/ibmdb/python-ibmdb)
- [ibm_db_dbi](https://github.com/ibmdb/python-ibmdb)
### ODBC
- [pyodbc](https://github.com/mkleehammer/pyodbc)
- [pypyodbc](https://github.com/pypyodbc/pypyodbc)
### Kingbase
- ksycopg2

# Further references (partly outdated)
- [List of Python DB interfaces](https://wiki.python.org/moin/DatabaseInterfaces)
- [Python DB programming](https://wiki.python.org/moin/DatabaseProgramming)