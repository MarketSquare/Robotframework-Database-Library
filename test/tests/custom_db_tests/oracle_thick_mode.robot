*** Settings ***
Documentation    Tests of switching between thin and thick mode of oracledb client.
...    Require the oracle client libraries installed.
...    See more here: https://python-oracledb.readthedocs.io/en/latest/user_guide/initialization.html#initialization

Resource    ../../resources/common.resource
Test Teardown    Drop Tables And Disconnect


*** Variables ***
${DB_MODULE}            oracledb
${DB_HOST}              127.0.0.1
${DB_PORT}              1521
${DB_PASS}              pass
${DB_USER}              db_user
${DB_NAME}              db
${ORACLE_LIB_DIR}       ${EMPTY}


*** Test Cases ***
Thick Mode Without Client Dir Specified
    [Documentation]    No client dir --> oracledb will search it in usual places
    Connect And Run Simple Query    driverMode=thick

Thin Mode - Default
    [Documentation]    No mode specified --> thin mode is used
    Connect And Run Simple Query

Thin Mode Explicitely Specified
    [Documentation]    Thin mode specified --> thin mode is used
    Connect And Run Simple Query  driverMode=thin

Thick Mode With Client Dir Specified
    [Documentation]    Client dir specified --> oracledb will search it in this place
    Connect And Run Simple Query    driverMode=thick,lib_dir=${ORACLE_LIB_DIR}

Wrong Mode
    [Documentation]    Wrong mode --> proper error message from the library
    Run Keyword And Expect Error    ValueError: Invalid Oracle client mode provided: wrong
    ...    Connect And Run Simple Query    driverMode=wrong

Thick Mode With Wrong Client Dir
    [Documentation]    Wrong mode --> proper error message from oracledb module
    Run Keyword And Expect Error    expected_error
    ...    Connect And Run Simple Query    driverMode=thick,lib_dir=C:/WRONG


*** Keywords ***
Connect And Run Simple Query
    [Documentation]    Connect using usual params and client mode if provided
    [Arguments]    &{Extra params}
    Connect To Database
    ...    ${DB_MODULE}
    ...    ${DB_NAME}
    ...    ${DB_USER}
    ...    ${DB_PASS}
    ...    ${DB_HOST}
    ...    ${DB_PORT}
    ...    &{Extra params}
    Create Person Table
    Query    SELECT * FROM person

Drop Tables And Disconnect
    [Documentation]    Clean data and disconnect
    Drop Tables Person And Foobar
    Disconnect From Database
