*** Settings ***
Documentation       Tests for assertion keywords with retry mechanism

Resource            ../../resources/common.resource

Suite Setup         Connect To DB And Prepare Data
Suite Teardown      Delete Data And Disconnect
Test Setup          Save Start Time

*** Variables ***
${Timeout}    ${3}
${Tolerance}    ${0.5}
${Request}    SELECT first_name FROM person

*** Test Cases ***
Check Query Results With Timeout - Fast If DB Ready    
    Check Query Result    ${Request}    contains   Allan    retry_timeout=${Timeout} seconds
    ${End time}=    Get Current Date
    ${Execution time}=    Subtract Date From Date    ${End time}    ${START_TIME}    
    Should Be True   0 <= $Execution_time <= $Tolerance

Check Query Results With Timeout - Slow If Result Wrong    
    Run Keyword And Expect Error    Wrong query result: 'Franz Allan' (str) should contain 'Blah' (str)
    ...    Check Query Result    ${Request}    contains   Blah    retry_timeout=${Timeout} seconds   retry_pause=1s
    ${End time}=    Get Current Date
    ${Execution time}=    Subtract Date From Date    ${End time}    ${START_TIME}    
    Should Be True   $Timeout <= $Execution_time <= $Timeout + $Tolerance

Check Query Results With Timeout - Slow If Row Count Wrong    
    Run Keyword And Expect Error    Checking row '5' is not possible, as query results contain 2 rows only!
    ...    Check Query Result    ${Request}    contains   Blah    row=5    retry_timeout=${Timeout} seconds
    ${End time}=    Get Current Date
    ${Execution time}=    Subtract Date From Date    ${End time}    ${START_TIME}
    Should Be True   $Timeout <= $Execution_time <= $Timeout + $Tolerance

Check Row Count With Timeout - Fast If DB Ready    
    Check Row Count    ${Request}    ==   2    retry_timeout=${Timeout} seconds
    ${End time}=    Get Current Date
    ${Execution time}=    Subtract Date From Date    ${End time}    ${START_TIME}    
    Should Be True   0 <= $Execution_time <= $Tolerance

Check Row Count With Timeout - Slow If Result Wrong    
    Run Keyword And Expect Error    Wrong row count: '2' (int) should be greater than '5' (int)
    ...    Check Row Count    ${Request}    >   5    retry_timeout=${Timeout} seconds   retry_pause=1s
    ${End time}=    Get Current Date
    ${Execution time}=    Subtract Date From Date    ${End time}    ${START_TIME}    
    Should Be True   $Timeout <= $Execution_time <= $Timeout + $Tolerance

*** Keywords ***
Connect To DB And Prepare Data
    Connect To DB
    Create Person Table And Insert Data

Delete Data And Disconnect
    Drop Tables Person And Foobar
    Disconnect From Database

Save Start Time
    ${START_TIME}=    Get Current Date
    Set Suite Variable    ${START_TIME}
