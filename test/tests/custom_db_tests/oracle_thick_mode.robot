*** Settings ***
Documentation    Tests of switching between thin and thick mode of oracledb client.
...    Require the oracle client libraries installed.
...    See more here: https://python-oracledb.readthedocs.io/en/latest/user_guide/initialization.html#initialization

Resource    ../../resources/common.resource


*** Test Cases ***
Thin Mode - Default
    [Documentation]    No mode specified --> thin mode is used
    Connect And Run Simple Query

Thin Mode Explicitely Specified
    [Documentation]    Thin mode specified --> thin mode is used
    Connect And Run Simple Query  driverMode=thin

Thick Mode Without Client Dir Specified
    [Documentation]    No client dir --> oracledb will search it in usual places
    Connect And Run Simple Query    driverMode=thick

Thick Mode With Client Dir Specified
    [Documentation]    Client dir specified --> oracledb will search it in this place
    Connect And Run Simple Query    driverMode=thick,lib_dir=

Wrong Mode
    [Documentation]    Wrong mode --> proper error message from the library
    Run Keyword And Expect Error    Invalid Oracle client mode provided: wrong
    ...    Connect And Run Simple Query    driverMode=wrong

Thick Mode With Wrong Client Dir
    [Documentation]    Wrong mode --> proper error message from oracledb module
    Run Keyword And Expect Error    expected_error
    ...    Connect And Run Simple Query    driverMode=thick,lib_dir=C:\WRONG


*** Keywords ***
Connect And Run Simple Query
    [Documentation]    Connect using usual params and client mode if provided
    [Arguments]    &{Extra params}
    Connect To Database
    ...    oracledb
    ...    127.0.0.1
    ...    1521
    ...    db
    ...    db_user
    ...    pass
    ...    &{Extra params}
    Create Person Table
    Query    SELECT * FROM person
