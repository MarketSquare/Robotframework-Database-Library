*** Settings ***
Documentation       Test that queries results are logged as HTML table.

Resource            ../../resources/common.resource

Suite Setup         Connect To DB
Suite Teardown      Disconnect From Database


*** Test Cases ***
Example test
    Create Person Table And Insert Data
    Query    SELECT * FROM person    log_results=${True}
    Query    SELECT COUNT(*) FROM person    log_results=${True}
    [Teardown]    Drop Tables Person And Foobar
