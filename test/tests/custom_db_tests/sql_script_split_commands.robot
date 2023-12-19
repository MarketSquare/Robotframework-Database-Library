*** Settings ***
Documentation    Tests for the parameter _split_ in the keyword
...    _Execute SQL Script_ - special for the issue #184:
...    https://github.com/MarketSquare/Robotframework-Database-Library/issues/184

Resource            ../../resources/common.resource
Suite Setup         Connect To DB
Suite Teardown      Disconnect From Database
Test Setup          Create Person Table
Test Teardown       Drop Tables Person And Foobar


*** Test Cases ***
Split Commands
    [Documentation]    Such a simple script works always,
    ...    just check if the logs if the parameter value was processed properly
    Execute Sql Script    ${CURDIR}/../../resources/insert_data_in_person_table.sql    split=True

Don't Split Commands
    [Documentation]    Running such a script as a single statement works for PostgreSQL,
    ...    but fails in Oracle. Check in the logs if the splitting was disabled.
    Execute Sql Script    ${CURDIR}/../../resources/insert_data_in_person_table.sql    split=False
