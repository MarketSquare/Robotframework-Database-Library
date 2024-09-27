*** Settings ***
Documentation    Tests of switching between thin and thick mode of oracledb client.
...    Require the oracle client libraries installed.
...    See more here: https://python-oracledb.readthedocs.io/en/latest/user_guide/initialization.html#initialization
...
...    Due to current limitations of the oracledb module it's not possible to switch between thick and thin modes
...    during a test execution session - even in different suites.
...    So theses tests should be run separated only.

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
    Connect And Run Simple Query    oracle_driver_mode=thick

Thick Mode With Client Dir Specified
    [Documentation]    Client dir specified --> oracledb will search it in this place
    Connect And Run Simple Query    oracle_driver_mode=thick,lib_dir=${ORACLE_LIB_DIR}

Thin Mode - Default
    [Documentation]    No mode specified --> thin mode is used
    Connect And Run Simple Query

Thin Mode Explicitely Specified
    [Documentation]    Thin mode specified --> thin mode is used
    Connect And Run Simple Query  oracle_driver_mode=thin

Wrong Mode
    [Documentation]    Wrong mode --> proper error message from the library
    Run Keyword And Expect Error    ValueError: Invalid Oracle client mode provided: wrong
    ...    Connect And Run Simple Query    oracle_driver_mode=wrong


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
