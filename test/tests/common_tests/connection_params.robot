*** Settings ***
Documentation       Tests for the basic _Connect To Database_ keyword - with and without config files.
...    The parameter handling is partly DB module specific.

Resource            ../../resources/common.resource

Test Setup          Skip If    $DB_MODULE == "sqlite3"
Test Teardown       Disconnect From Database

*** Variables ***
&{Errors psycopg2}
...    missing basic params=OperationalError: connection to server on socket *
...    invalid custom param=ProgrammingError: invalid dsn: invalid connection option "blah"*
&{Errors oracledb}
...    missing basic params=DatabaseError: DPY-4001: no credentials specified
...    invalid custom param=TypeError: connect() got an unexpected keyword argument 'blah'
&{Errors pymssql}
...    missing basic params=OperationalError: (20002, b'DB-Lib error message 20002, severity 9*
...    invalid custom param=TypeError: connect() got an unexpected keyword argument 'blah'
&{Errors pymysql}
...    missing basic params=OperationalError: (1045, "Access denied*
...    invalid custom param=TypeError: __init__() got an unexpected keyword argument 'blah'
&{Errors pyodbc}
...    missing basic params=REGEXP: InterfaceError.*Data source name not found and no default driver specified.*
...    invalid custom param=TypeError: connect() got an unexpected keyword argument 'blah'

&{Errors}
...    psycopg2=${Errors psycopg2}
...    oracledb=${Errors oracledb}
...    pymssql=${Errors pymssql}
...    pymysql=${Errors pymysql}
...    pyodbc=${Errors pyodbc}


*** Test Cases ***
Mandatory params can't be missing
    Run Keyword And Expect Error    
    ...    ValueError: Required parameter 'dbapiModuleName' was not provided*
    ...    Connect To Database    dbName=${DB_NAME}

All basic params, no config file
    Connect To Database
    ...    dbapiModuleName=${DB_MODULE}
    ...    dbName=${DB_NAME}
    ...    dbUsername=${DB_USER}
    ...    dbPassword=${DB_PASS}
    ...    dbHost=${DB_HOST}
    ...    dbPort=${DB_PORT}
    ...    dbDriver=${DB_DRIVER}

Missing basic params are accepted, error from Python DB module
    Run Keyword And Expect Error    
    ...    ${Errors}[${DB_MODULE}][missing basic params]
    ...    Connect To Database
    ...    dbapiModuleName=${DB_MODULE}

Custom params as keyword args - valid
    Connect To Database
    ...    dbapiModuleName=${DB_MODULE}
    ...    dbName=${DB_NAME}    
    ...    dbHost=${DB_HOST}
    ...    dbPort=${DB_PORT}
    ...    dbDriver=${DB_DRIVER}
    ...    user=${DB_USER}
    ...    password=${DB_PASS}

Custom params as keyword args - invalid, error from Python DB module
    Run Keyword And Expect Error    
    ...    ${Errors}[${DB_MODULE}][invalid custom param]
    ...    Connect To Database
    ...    dbapiModuleName=${DB_MODULE}
    ...    dbName=${DB_NAME}    
    ...    dbHost=${DB_HOST}
    ...    dbPort=${DB_PORT}
    ...    dbUsername=${DB_USER}
    ...    dbPassword=${DB_PASS}
    ...    dbDriver=${DB_DRIVER}
    ...    blah=blah

All basic params in config file
    Connect Using Config File    ${DB_MODULE}/simple_default_alias

Missing basic params in config file are accepted, error from Python DB module
    Run Keyword And Expect Error    
    ...    ${Errors}[${DB_MODULE}][missing basic params]
    ...    Connect Using Config File    
    ...    ${DB_MODULE}/some_basic_params_missing

Custom params from config file - valid
    Connect Using Config File    ${DB_MODULE}/valid_custom_params

Custom params from config file - invalid, error from Python DB module
    Run Keyword And Expect Error    
    ...    ${Errors}[${DB_MODULE}][invalid custom param]
    ...    Connect Using Config File    ${DB_MODULE}/invalid_custom_params

Custom params as keyword args combined with custom params from config file
    Connect Using Config File    ${DB_MODULE}/custom_param_password    
    ...    user=${DB_USER}
    

Keyword args override config file values - basic params
    Connect Using Config File    ${DB_MODULE}/wrong_password
    ...    dbPassword=${DB_PASS}

Keyword args override config file values - custom params
    Connect Using Config File    ${DB_MODULE}/valid_custom_params
    ...    user=${DB_USER}

Oracle specific - basic params, no config file, driverMode
    Skip If    $DB_MODULE != "oracledb"
    Connect To Database
    ...    dbapiModuleName=${DB_MODULE}
    ...    dbName=${DB_NAME}
    ...    dbUsername=${DB_USER}
    ...    dbPassword=${DB_PASS}
    ...    dbHost=${DB_HOST}
    ...    dbPort=${DB_PORT}
    ...    driverMode=thin

Oracle specific - thick mode in config file - invalid
    [Documentation]    Invalid as mode switch during test execution is not supported
    ...    This test must run the last one in the suite, after others used thin mode already.
    Skip If    $DB_MODULE != "oracledb"
    Run Keyword And Expect Error    ProgrammingError: DPY-2019: python-oracledb thick mode cannot be used because a thin mode connection has already been created
    ...    Connect Using Config File    ${DB_MODULE}/thick_mode


MSSQL / MySQL / PyODBC specific - charset as keyword argument
    Skip If    $DB_MODULE not in ["pymssql", "pymysql", "pyodbc"]
    Connect To Database
    ...    dbapiModuleName=${DB_MODULE}
    ...    dbName=${DB_NAME}
    ...    dbUsername=${DB_USER}
    ...    dbPassword=${DB_PASS}
    ...    dbHost=${DB_HOST}
    ...    dbPort=${DB_PORT}
    ...    dbDriver=${DB_DRIVER}
    ...    dbCharset=LATIN1

MSSQL / PyODBC specific - charset in config file - invalid
    Skip If    $DB_MODULE not in ["pymssql", "pyodbc"]
    Run Keyword And Expect Error    OperationalError: (20002, b'Unknown error')
    ...    Connect Using Config File    ${DB_MODULE}/charset_invalid

MySQL specific - charset in config file - invalid
    Skip If    $DB_MODULE not in ["pymysql"]
    Run Keyword And Expect Error    AttributeError: 'NoneType' object has no attribute 'encoding'
    ...    Connect Using Config File    ${DB_MODULE}/charset_invalid


SQlite specific - connection params as custom keyword args
    [Setup]    Skip If    $DB_MODULE != "sqlite3"
    Remove File    ${DBName}.db
    Connect To Database
    ...    dbapiModuleName=${DB_MODULE}
    ...    database=./${DBName}.db
    ...    isolation_level=${EMPTY}

SQlite specific - custom connection params in config file
    [Setup]    Skip If    $DB_MODULE != "sqlite3"
    Remove File    ${DBName}.db
    Connect Using Config File    ${DB_MODULE}/simple_default_alias
