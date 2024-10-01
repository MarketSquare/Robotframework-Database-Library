*** Settings ***
Documentation    Tests for parameters used when importing the library

*** Test Cases ***
Import Without Parameters Is Valid
    Import Library    DatabaseLibrary

Log Query Results Params Cause No Crash
    Import Library    DatabaseLibrary    log_query_results=False    log_query_results_head=0

Log Query Results Head - Negative Value Not Allowed
    Run Keyword And Expect Error
    ...    STARTS: Initializing library 'DatabaseLibrary' with arguments [ log_query_results_head=-1 ] failed: ValueError: Wrong log head value provided: -1. The value can't be negative!
    ...    Import Library    DatabaseLibrary    log_query_results_head=-1