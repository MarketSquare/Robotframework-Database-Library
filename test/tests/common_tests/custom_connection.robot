*** Settings ***
Documentation       Keyword 'Connect To Database Using Custom Params' should work properly
...                 for different DB modules.

Resource            ../../resources/common.resource

Test Teardown       Disconnect From Database


*** Variables ***
${CONNECTION_STRING}    ${EMPTY}    # the variable is set dynamically depending on the current DB module


*** Test Cases ***
Connect Using Custom Connection String
    [Documentation]    Connection string provided without additional quotes should work properly.
    ${Connection String}=    Build Connection String
    Connect To Database Using Custom Connection String    ${DB_MODULE}    ${Connection String}

Connect Using Custom Params
    IF    "${DB_MODULE}" == "oracledb"
        ${Params}=    Catenate
        ...    user='${DB_USER}',
        ...    password='${DB_PASS}',
        ...    dsn='${DB_HOST}:${DB_PORT}/${DB_NAME}'
    ELSE IF    "${DB_MODULE}" == "pyodbc"
        ${Params}=    Catenate
        ...    driver='${DB_DRIVER}',
        ...    charset='${DB_CHARSET}',
        ...    database='${DB_NAME}',
        ...    user='${DB_USER}',
        ...    password='${DB_PASS}',
        ...    host='${DB_HOST}',
        ...    port=${DB_PORT}
    ELSE IF    "${DB_MODULE}" == "sqlite3"
        ${Params}=    Catenate
        ...    database="./${DBName}.db",
        ...    isolation_level=None
    ELSE
        ${Params}=    Catenate
        ...    database='${DB_NAME}',
        ...    user='${DB_USER}',
        ...    password='${DB_PASS}',
        ...    host='${DB_HOST}',
        ...    port=${DB_PORT}
    END
    Connect To Database Using Custom Params
    ...    ${DB_MODULE}
    ...    ${Params}
