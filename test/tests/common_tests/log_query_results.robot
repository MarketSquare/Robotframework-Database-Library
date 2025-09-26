*** Settings ***
Documentation       Tests for keywords controlling the logging query results

Resource            ../../resources/common.resource

Suite Setup         Connect To DB
Suite Teardown      Disconnect From Database
Test Setup          Create Person Table And Insert Data
Test Teardown       Drop Tables Person And Foobar

*** Test Cases ***
Calling The Keyword Causes No Crash
    Set Logging Query Results    enabled=False
    Set Logging Query Results    enabled=True    log_head=0
    Set Logging Query Results    log_head=30

Check Max Height For Long Tables
    FOR    ${id}    IN RANGE    10   50
        Execute Sql String    INSERT INTO person VALUES(${id}, 'Somebody that', 'I used to know');      
    END
    Query    SELECT * FROM person