*** Settings ***
Documentation       Set DB connection variables based on a single global variable
...                 which can be passed from outside (e.g. VS Code lauch config)

Suite Setup         Set DB Variables


*** Variables ***
${GLOBAL_DB_SELECTOR}       None


*** Keywords ***
Set DB Variables
    [Documentation]    These are custom connection params for databases,
    ...    running locally on the developer's machine.
    ...    You might need other values for your databases!
    IF    "${GLOBAL_DB_SELECTOR}" == "PostgreSQL"
        Set Global Variable    ${DB_MODULE_MODE}    standard
        Set Global Variable    ${DB_MODULE}    psycopg2
        Set Global Variable    ${DB_HOST}    127.0.0.1
        Set Global Variable    ${DB_PORT}    5432
        Set Global Variable    ${DB_NAME}    db
        Set Global Variable    ${DB_USER}    db_user
        Set Global Variable    ${DB_PASS}    pass
    ELSE IF    "${GLOBAL_DB_SELECTOR}" == "oracledb"
        Set Global Variable    ${DB_MODULE_MODE}    standard
        Set Global Variable    ${DB_MODULE}    oracledb
        Set Global Variable    ${DB_HOST}    127.0.0.1
        Set Global Variable    ${DB_PORT}    1521
        Set Global Variable    ${DB_NAME}    db
        Set Global Variable    ${DB_USER}    db_user
        Set Global Variable    ${DB_PASS}    pass
    ELSE IF    "${GLOBAL_DB_SELECTOR}" == "cx_Oracle"
        Set Global Variable    ${DB_MODULE_MODE}    standard
        Set Global Variable    ${DB_MODULE}    cx_Oracle
        Set Global Variable    ${DB_HOST}    127.0.0.1
        Set Global Variable    ${DB_PORT}    1521
        Set Global Variable    ${DB_NAME}    db
        Set Global Variable    ${DB_USER}    db_user
        Set Global Variable    ${DB_PASS}    pass
    ELSE IF    "${GLOBAL_DB_SELECTOR}" == "SQLite"
        Set Global Variable    ${DB_MODULE_MODE}    custom
        Set Global Variable    ${DB_MODULE}    sqlite3
    ELSE IF    "${GLOBAL_DB_SELECTOR}" == "IBM_DB2"
        Set Global Variable    ${DB_MODULE_MODE}    standard
        Set Global Variable    ${DB_MODULE}    ibm_db_dbi
        Set Global Variable    ${DB_HOST}    127.0.0.1
        Set Global Variable    ${DB_PORT}    50000
        Set Global Variable    ${DB_NAME}    db
        Set Global Variable    ${DB_USER}    db_user
        Set Global Variable    ${DB_PASS}    pass
    ELSE IF    "${GLOBAL_DB_SELECTOR}" == "Teradata"
        Set Global Variable    ${DB_MODULE_MODE}    standard
        Set Global Variable    ${DB_MODULE}    teradata
        Set Global Variable    ${DB_HOST}    192.168.0.231
        Set Global Variable    ${DB_PORT}    1025
        Set Global Variable    ${DB_NAME}    db
        Set Global Variable    ${DB_USER}    dbc
        Set Global Variable    ${DB_PASS}    dbc
    ELSE IF    "${GLOBAL_DB_SELECTOR}" == "MySQL_pymysql"
        Set Global Variable    ${DB_MODULE_MODE}    standard
        Set Global Variable    ${DB_MODULE}    pymysql
        Set Global Variable    ${DB_HOST}    127.0.0.1
        Set Global Variable    ${DB_PORT}    3306
        Set Global Variable    ${DB_NAME}    db
        Set Global Variable    ${DB_USER}    db_user
        Set Global Variable    ${DB_PASS}    pass
    ELSE IF    "${GLOBAL_DB_SELECTOR}" == "MySQL_pyodbc"
        Set Global Variable    ${DB_MODULE_MODE}    standard
        Set Global Variable    ${DB_MODULE}    pyodbc
        Set Global Variable    ${DB_HOST}    127.0.0.1
        Set Global Variable    ${DB_PORT}    3306
        Set Global Variable    ${DB_NAME}    db
        Set Global Variable    ${DB_USER}    db_user
        Set Global Variable    ${DB_PASS}    pass
    ELSE IF    "${GLOBAL_DB_SELECTOR}" == "MSSQL"
        Set Global Variable    ${DB_MODULE_MODE}    standard
        Set Global Variable    ${DB_MODULE}    pymssql
        Set Global Variable    ${DB_HOST}    127.0.0.1
        Set Global Variable    ${DB_PORT}    1433
        Set Global Variable    ${DB_NAME}    db
        Set Global Variable    ${DB_USER}    SA
        Set Global Variable    ${DB_PASS}    MyPass1234!
    ELSE IF    "${GLOBAL_DB_SELECTOR}" == "Excel"
        Set Global Variable    ${DB_MODULE_MODE}    standard
        Set Global Variable    ${DB_MODULE}    excel
        Set Global Variable    ${DB_NAME}    db
    ELSE IF    "${GLOBAL_DB_SELECTOR}" == "Excel_RW"
        Set Global Variable    ${DB_MODULE_MODE}    standard
        Set Global Variable    ${DB_MODULE}    excelrw
        Set Global Variable    ${DB_NAME}    db
    END
