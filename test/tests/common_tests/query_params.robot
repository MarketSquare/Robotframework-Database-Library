*** Settings ***
Documentation       Keywords with query params as separate arguments work across all databases.

Resource            ../../resources/common.resource

Suite Setup         Connect To DB And Build Query
Suite Teardown      Disconnect From Database
Test Setup          Create Person Table And Insert Data
Test Teardown       Drop Tables Person And Foobar


*** Variables ***
@{SINGLE_PARAM}    Franz Allan
@{MULTI_PARAM}     Jerry    Schneider


*** Keywords ***
Connect To DB And Build Query
    Connect To DB
    Build Query Strings With Params

Build Query Strings With Params
    ${placeholder}=    Set Variable    %s
    IF  "${DB_MODULE}" in ["oracledb", "cx_Oracle"]
        ${placeholder}=    Set Variable    :id
    ELSE IF  "${DB_MODULE}" in ["sqlite3", "pyodbc"]
        ${placeholder}=    Set Variable    ?
    END
    Set Suite Variable    ${QUERY_SINGLE_PARAM}    SELECT id FROM person WHERE FIRST_NAME=${placeholder}
    Set Suite Variable    ${QUERY_MULTI_PARAM}    ${QUERY_SINGLE_PARAM} AND LAST_NAME=${placeholder}


*** Test Cases ***
Query Single Param
    ${out}=    Query    ${QUERY_SINGLE_PARAM}    parameters=${SINGLE_PARAM}
    Length Should Be    ${out}    1

Query Multiple Params
    ${out}=    Query    ${QUERY_MULTI_PARAM}    parameters=${MULTI_PARAM}
    Length Should Be    ${out}    1

Row Count
    ${out}=    Row Count    ${QUERY_SINGLE_PARAM}    parameters=${SINGLE_PARAM}
    Should Be Equal As Strings    ${out}    1

Description
    ${out}=    Description    ${QUERY_SINGLE_PARAM}    parameters=${SINGLE_PARAM}
    Length Should Be    ${out}    1

Execute SQL String
    Execute Sql String    ${QUERY_SINGLE_PARAM}    parameters=${SINGLE_PARAM}

Check If Exists In DB
    Check If Exists In Database    ${QUERY_SINGLE_PARAM}    parameters=${SINGLE_PARAM}

Check If Not Exists In DB
    @{Wrong params}=    Create List    Joe
    Check If Not Exists In Database    ${QUERY_SINGLE_PARAM}    parameters=${Wrong params}

Row Count is 0
    @{Wrong params}=    Create List    Joe
    Row Count is 0    ${QUERY_SINGLE_PARAM}    parameters=${Wrong params}

Row Count is Equal to X
    Row Count is Equal to X    ${QUERY_SINGLE_PARAM}    1    parameters=${SINGLE_PARAM}

Row Count is Less Than X
    Row Count is Less Than X    ${QUERY_SINGLE_PARAM}    5    parameters=${SINGLE_PARAM}

Row Count is Greater Than X
    Row Count is Greater Than X    ${QUERY_SINGLE_PARAM}    0    parameters=${SINGLE_PARAM}
