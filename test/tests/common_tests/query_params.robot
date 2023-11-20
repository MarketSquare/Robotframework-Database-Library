*** Settings ***
Documentation       Keywords with query params as seperate arguments work across all databases.

Resource            ../../resources/common.resource

Suite Setup         Connect To DB And Build Query
Suite Teardown      Disconnect From Database
Test Setup          Create Person Table And Insert Data
Test Teardown       Drop Tables Person And Foobar


*** Variables ***
@{PARAMS}    Franz Allan


*** Keywords ***
Connect To DB And Build Query
    Connect To DB
    Build Query String With Params

Build Query String With Params
    ${sql}=    Set Variable    SELECT id FROM person WHERE FIRST_NAME=
    IF  "${DB_MODULE}" in ["oracledb", "cx_Oracle"]
        ${sql}=    Catenate    ${sql}    :id
    ELSE IF  "${DB_MODULE}" in ["sqlite3", "pyodbc"]
        ${sql}=    Catenate    ${sql}    ?
    ELSE
        ${sql}=    Catenate    ${sql}    %s
    END
    Set Suite Variable    ${QUERY}    ${sql}


*** Test Cases ***
Query
    ${out}=    Query    ${QUERY}    parameters=${PARAMS}
    Length Should Be    ${out}    1

Row Count
    ${out}=    Row Count    ${QUERY}    parameters=${PARAMS}
    Should Be Equal As Strings    ${out}    1

Description
    ${out}=    Description    ${QUERY}    parameters=${PARAMS}
    Length Should Be    ${out}    1

Execute SQL String
    Execute Sql String    ${QUERY}    parameters=${PARAMS}

Check If Exists In DB
    Check If Exists In Database    ${QUERY}    parameters=${PARAMS}

Check If Not Exists In DB
    @{Wrong params}=    Create List    Joe
    Check If Not Exists In Database    ${QUERY}    parameters=${Wrong params}

Row Count is 0
    @{Wrong params}=    Create List    Joe
    Row Count is 0    ${QUERY}    parameters=${Wrong params}

Row Count is Equal to X
    Row Count is Equal to X    ${QUERY}    1    parameters=${PARAMS}

Row Count is Less Than X
    Row Count is Less Than X    ${QUERY}    5    parameters=${PARAMS}

Row Count is Greater Than X
    Row Count is Greater Than X    ${QUERY}    0    parameters=${PARAMS}
