*** Settings ***
Documentation       The result of the "description" request is very different depending on the database

Resource            ../../resources/common.resource

Suite Setup         Connect To DB
Suite Teardown      Disconnect From Database
Test Setup          Create Tables Person And Foobar
Test Teardown       Drop Tables Person And Foobar


*** Test Cases ***
Verify Person Description
    @{queryResults} =    Description    SELECT * FROM person
    Log Many    @{queryResults}
    Length Should Be    ${queryResults}    3
    IF    "${DB_MODULE}" == "oracledb"
        Should Be Equal As Strings    ${queryResults}[0]    ('ID', <DbType DB_TYPE_NUMBER>, 39, None, 38, 0, False)
        Should Be Equal As Strings
        ...    ${queryResults}[1]
        ...    ('FIRST_NAME', <DbType DB_TYPE_VARCHAR>, 20, 20, None, None, True)
        Should Be Equal As Strings
        ...    ${queryResults}[2]
        ...    ('LAST_NAME', <DbType DB_TYPE_VARCHAR>, 20, 20, None, None, True)
    ELSE IF    "${DB_MODULE}" == "sqlite3"
        Should Be Equal As Strings    ${queryResults}[0]    ('id', None, None, None, None, None, None)
        Should Be Equal As Strings    ${queryResults}[1]    ('FIRST_NAME', None, None, None, None, None, None)
        Should Be Equal As Strings    ${queryResults}[2]    ('LAST_NAME', None, None, None, None, None, None)
    ELSE IF    "${DB_MODULE}" == "ibm_db_dbi"
        Should Be True    "${queryResults}[0]".startswith("['ID', DBAPITypeObject(")
        Should Be True    "${queryResults}[0]".endswith("), 11, 11, 10, 0, False]")
        Should Be True    "INT" in "${queryResults}[0]"
        Should Be True    "${queryResults}[1]".startswith("['FIRST_NAME', DBAPITypeObject(")
        Should Be True    "${queryResults}[1]".endswith("), 20, 20, 20, 0, True]")
        Should Be True    "VARCHAR" in "${queryResults}[1]"
        Should Be True    "${queryResults}[2]".startswith("['LAST_NAME', DBAPITypeObject(")
        Should Be True    "${queryResults}[2]".endswith("), 20, 20, 20, 0, True]")
        Should Be True    "VARCHAR" in "${queryResults}[2]"
    ELSE IF    "${DB_MODULE}" == "teradata"
        Should Be Equal As Strings    ${queryResults}[0]    ('id', <class 'decimal.Decimal'>, None, 10, 0, None, 0)
        Should Be Equal As Strings    ${queryResults}[1]    ('FIRST_NAME', <class 'str'>, None, 20, 0, None, 1)
        Should Be Equal As Strings    ${queryResults}[2]    ('LAST_NAME', <class 'str'>, None, 20, 0, None, 1)
    ELSE IF    "${DB_MODULE}" == "psycopg2"
        Should Be Equal As Strings    ${queryResults}[0]    Column(name='id', type_code=23)
        Should Be Equal As Strings    ${queryResults}[1]    Column(name='first_name', type_code=1043)
        Should Be Equal As Strings    ${queryResults}[2]    Column(name='last_name', type_code=1043)
    ELSE IF    "${DB_MODULE}" == "pymysql"
        Should Be Equal As Strings    ${queryResults}[0]    ('id', 3, None, 11, 11, 0, False)
        Should Be Equal As Strings    ${queryResults}[1]    ('FIRST_NAME', 253, None, 80, 80, 0, True)
        Should Be Equal As Strings    ${queryResults}[2]    ('LAST_NAME', 253, None, 80, 80, 0, True)
    ELSE IF    "${DB_MODULE}" == "pyodbc"
        Should Be Equal As Strings    ${queryResults}[0]    ('id', <class 'int'>, None, 10, 10, 0, False)
        Should Be Equal As Strings    ${queryResults}[1]    ('FIRST_NAME', <class 'str'>, None, 20, 20, 0, True)
        Should Be Equal As Strings    ${queryResults}[2]    ('LAST_NAME', <class 'str'>, None, 20, 20, 0, True)
    ELSE IF    "${DB_MODULE}" == "pymssql"
        Should Be Equal As Strings    ${queryResults}[0]    ('id', 3, None, None, None, None, None)
        Should Be Equal As Strings    ${queryResults}[1]    ('FIRST_NAME', 1, None, None, None, None, None)
        Should Be Equal As Strings    ${queryResults}[2]    ('LAST_NAME', 1, None, None, None, None, None)
    ELSE
        Should Be Equal As Strings    ${queryResults}[0]    Column(name='id', type_code=23)
        Should Be Equal As Strings    ${queryResults}[1]    Column(name='first_name', type_code=1043)
        Should Be Equal As Strings    ${queryResults}[2]    Column(name='last_name', type_code=1043)
    END

Verify Foobar Description
    @{queryResults} =    Description    SELECT * FROM foobar
    Log Many    @{queryResults}
    Length Should Be    ${queryResults}    2
    IF    "${DB_MODULE}" == "oracledb"
        Should Be Equal As Strings    ${queryResults}[0]    ('ID', <DbType DB_TYPE_NUMBER>, 39, None, 38, 0, False)
        Should Be Equal As Strings
        ...    ${queryResults}[1]
        ...    ('FIRST_NAME', <DbType DB_TYPE_VARCHAR>, 30, 30, None, None, False)
    ELSE IF    "${DB_MODULE}" == "sqlite3"
        Should Be Equal As Strings    ${queryResults}[0]    ('id', None, None, None, None, None, None)
        Should Be Equal As Strings    ${queryResults}[1]    ('FIRST_NAME', None, None, None, None, None, None)
    ELSE IF    "${DB_MODULE}" == "ibm_db_dbi"
        Should Be True    "${queryResults}[0]".startswith("['ID', DBAPITypeObject(")
        Should Be True    "${queryResults}[0]".endswith("), 11, 11, 10, 0, False]")
        Should Be True    "INT" in "${queryResults}[0]"
        Should Be True    "${queryResults}[1]".startswith("['FIRST_NAME', DBAPITypeObject(")
        Should Be True    "${queryResults}[1]".endswith("), 30, 30, 30, 0, False]")
        Should Be True    "VARCHAR" in "${queryResults}[1]"
    ELSE IF    "${DB_MODULE}" == "teradata"
        Should Be Equal As Strings    ${queryResults}[0]    ('id', <class 'decimal.Decimal'>, None, 10, 0, None, 0)
        Should Be Equal As Strings    ${queryResults}[1]    ('FIRST_NAME', <class 'str'>, None, 30, 0, None, 0)
    ELSE IF    "${DB_MODULE}" == "psycopg2"
        Should Be Equal As Strings    ${queryResults}[0]    Column(name='id', type_code=23)
        Should Be Equal As Strings    ${queryResults}[1]    Column(name='first_name', type_code=1043)
    ELSE IF    "${DB_MODULE}" == "pymysql"
        Should Be Equal As Strings    ${queryResults}[0]    ('id', 3, None, 11, 11, 0, False)
        Should Be Equal As Strings    ${queryResults}[1]    ('FIRST_NAME', 253, None, 120, 120, 0, False)
    ELSE IF    "${DB_MODULE}" in "pyodbc"
        Should Be Equal As Strings    ${queryResults}[0]    ('id', <class 'int'>, None, 10, 10, 0, False)
        Should Be Equal As Strings    ${queryResults}[1]    ('FIRST_NAME', <class 'str'>, None, 30, 30, 0, False)
    ELSE IF    "${DB_MODULE}" == "pymssql"
        Should Be Equal As Strings    ${queryResults}[0]    ('id', 3, None, None, None, None, None)
        Should Be Equal As Strings    ${queryResults}[1]    ('FIRST_NAME', 1, None, None, None, None, None)
    ELSE
        Should Be Equal As Strings    ${queryResults}[0]    Column(name='id', type_code=23)
        Should Be Equal As Strings    ${queryResults}[1]    Column(name='first_name', type_code=1043)
    END
