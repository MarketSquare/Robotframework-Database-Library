*** Settings ***
Documentation       Tests for the basic _Connect To Database_ keyword - with and without config files.
...    The parameter handling is partly DB module specific.

Resource            ../../resources/common.resource

Test Setup          Skip If    $DB_MODULE == "sqlite3" or $DB_MODULE == "jaydebeapi"
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

&{Errors}
...    psycopg2=${Errors psycopg2}
...    oracledb=${Errors oracledb}
...    pymssql=${Errors pymssql}
...    pymysql=${Errors pymysql}
...    pyodbc=${Errors pyodbc}


*** Test Cases ***
Mandatory params can't be missing
    Run Keyword And Expect Error    
    ...    ValueError: Required parameter 'db_module' was not provided*
    ...    Connect To Database    db_name=${DB_NAME}

All basic params, no config file
    Connect To Database
    ...    db_module=${DB_MODULE}
    ...    db_name=${DB_NAME}
    ...    db_user=${DB_USER}
    ...    db_password=${DB_PASS}
    ...    db_host=${DB_HOST}
    ...    db_port=${DB_PORT}
    ...    odbc_driver=${DB_DRIVER}

Missing basic params are accepted, error from Python DB module
    Run Keyword And Expect Error    
    ...    ${Errors}[${DB_MODULE}][missing basic params]
    ...    Connect To Database
    ...    db_module=${DB_MODULE}

Custom params as keyword args - valid
    Connect To Database
    ...    db_module=${DB_MODULE}
    ...    db_name=${DB_NAME}    
    ...    db_host=${DB_HOST}
    ...    db_port=${DB_PORT}
    ...    odbc_driver=${DB_DRIVER}
    ...    user=${DB_USER}
    ...    password=${DB_PASS}

Custom params as keyword args - invalid, error from Python DB module
    Skip If    $DB_MODULE == "pyodbc"    
    ...    pyodbc doesn't always throw an error if some wrong parameter was provided
    Run Keyword And Expect Error    
    ...    ${Errors}[${DB_MODULE}][invalid custom param]
    ...    Connect To Database
    ...    db_module=${DB_MODULE}
    ...    db_name=${DB_NAME}    
    ...    db_host=${DB_HOST}
    ...    db_port=${DB_PORT}
    ...    db_user=${DB_USER}
    ...    db_password=${DB_PASS}
    ...    odbc_driver=${DB_DRIVER}
    ...    blah=blah

All basic params in config file
    Connect Using Config File    ${DB_MODULE}/simple_default_alias

Deprecated basic params in config file
    Connect Using Config File    ${DB_MODULE}/old_param_names

Missing basic params in config file are accepted, error from Python DB module
    Run Keyword And Expect Error    
    ...    ${Errors}[${DB_MODULE}][missing basic params]
    ...    Connect Using Config File    
    ...    ${DB_MODULE}/some_basic_params_missing

Custom params from config file - valid
    Connect Using Config File    ${DB_MODULE}/valid_custom_params

Custom params from config file - invalid, error from Python DB module
    Skip If    $DB_MODULE == "pyodbc"    
    ...    pyodbc doesn't always throw an error if some wrong parameter was provided
    Run Keyword And Expect Error    
    ...    ${Errors}[${DB_MODULE}][invalid custom param]
    ...    Connect Using Config File    ${DB_MODULE}/invalid_custom_params

Custom params as keyword args combined with custom params from config file
    Connect Using Config File    ${DB_MODULE}/custom_param_password    
    ...    user=${DB_USER}
    

Keyword args override config file values - basic params
    Connect Using Config File    ${DB_MODULE}/wrong_password
    ...    db_password=${DB_PASS}

Keyword args override config file values - custom params
    Connect Using Config File    ${DB_MODULE}/valid_custom_params
    ...    user=${DB_USER}

Oracle specific - basic params, no config file, oracle_driver_mode
    Skip If    $DB_MODULE != "oracledb"
    Connect To Database
    ...    db_module=${DB_MODULE}
    ...    db_name=${DB_NAME}
    ...    db_user=${DB_USER}
    ...    db_password=${DB_PASS}
    ...    db_host=${DB_HOST}
    ...    db_port=${DB_PORT}
    ...    oracle_driver_mode=thin

Oracle specific - thick mode in config file - invalid
    [Documentation]    Invalid as mode switch during test execution is not supported
    ...    This test must run the last one in the suite, after others used thin mode already.
    Skip If    $DB_MODULE != "oracledb"
    Run Keyword And Expect Error    ProgrammingError: DPY-2019: python-oracledb thick mode cannot be used *
    ...    Connect Using Config File    ${DB_MODULE}/thick_mode


MSSQL / MySQL / PyODBC specific - charset as keyword argument
    Skip If    $DB_MODULE not in ["pymssql", "pymysql", "pyodbc"]
    Connect To Database
    ...    db_module=${DB_MODULE}
    ...    db_name=${DB_NAME}
    ...    db_user=${DB_USER}
    ...    db_password=${DB_PASS}
    ...    db_host=${DB_HOST}
    ...    db_port=${DB_PORT}
    ...    odbc_driver=${DB_DRIVER}
    ...    db_charset=LATIN1

MSSQL specific - charset in config file - invalid
    Skip If    $DB_MODULE not in ["pymssql"]
    Run Keyword And Expect Error    OperationalError: (20002, b'Unknown error')
    ...    Connect Using Config File    ${DB_MODULE}/charset_invalid

MySQL specific - charset in config file - invalid
    Skip If    $DB_MODULE not in ["pymysql"]
    Run Keyword And Expect Error    AttributeError: 'NoneType' object has no attribute 'encoding'
    ...    Connect Using Config File    ${DB_MODULE}/charset_invalid

PyODBC specific - charset in config file - invalid
    Skip If    $DB_MODULE not in ["pyodbc"]
    Run Keyword And Expect Error    REGEXP: .*Unknown character set: 'wrong'.*
    ...    Connect Using Config File    ${DB_MODULE}/charset_invalid


SQlite specific - connection params as custom keyword args
    [Setup]    Skip If    $DB_MODULE != "sqlite3"
    Remove File    ${DBName}.db
    Connect To Database
    ...    db_module=${DB_MODULE}
    ...    database=./${DBName}.db
    ...    isolation_level=${EMPTY}

SQlite specific - custom connection params in config file
    [Setup]    Skip If    $DB_MODULE != "sqlite3"
    Remove File    ${DBName}.db
    Connect Using Config File    ${DB_MODULE}/simple_default_alias
