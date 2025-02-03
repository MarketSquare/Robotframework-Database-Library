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

Warn On Connection Overwrite Enabled
    Skip If    '${DB_MODULE}' != 'psycopg2'
    Import Library    DatabaseLibrary    warn_on_connection_overwrite=True        AS    MyDBLib
    FOR    ${counter}    IN RANGE    0    2
        MyDBLib.Connect To Database
        ...    db_module=${DB_MODULE}
        ...    db_name=${DB_NAME}
        ...    db_user=${DB_USER}
        ...    db_password=${DB_PASS}
        ...    db_host=${DB_HOST}
        ...    db_port=${DB_PORT}    
    END
    [Teardown]    MyDBLib.Disconnect From Database

Warn On Connection Overwrite Disabled
    Skip If    '${DB_MODULE}' != 'psycopg2'
    Import Library    DatabaseLibrary    warn_on_connection_overwrite=False    AS    MyDBLib2
    FOR    ${counter}    IN RANGE    0    2
        MyDBLib2.Connect To Database
        ...    db_module=${DB_MODULE}
        ...    db_name=${DB_NAME}
        ...    db_user=${DB_USER}
        ...    db_password=${DB_PASS}
        ...    db_host=${DB_HOST}
        ...    db_port=${DB_PORT}    
    END
    [Teardown]    MyDBLib2.Disconnect From Database