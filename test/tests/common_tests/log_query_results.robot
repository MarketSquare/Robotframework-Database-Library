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