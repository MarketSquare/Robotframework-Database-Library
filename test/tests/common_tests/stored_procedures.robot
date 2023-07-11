*** Settings ***
Resource            ../../resources/common.resource

Suite Setup         Connect To DB
Suite Teardown      Disconnect From Database
Test Setup          Create And Fill Tables And Stored Procedures
Test Teardown       Drop Tables Person And Foobar


*** Test Cases ***
Procedure Takes No Params
    ${param values}    ${result sets}=    Call Stored Procedure    no_params
    Length Should Be    ${param values}    0
    IF    "${DB_MODULE}" in ["psycopg2", "psycopg3"]
        Length Should Be    ${result sets}    1
        Should Be Equal As Strings    ${result sets}[0][0][0]    ${EMPTY}
    ELSE
        Length Should Be    ${result sets}    0
    END

Procedure Returns Single Value As Param
    IF    "${DB_MODULE}" in ["psycopg2", "psycopg3"]
        Skip    PostgreSQL doesn't return single values as params, only as result sets
    END
    IF    "${DB_MODULE}" in ["pymssql"]
        Skip    Returning values using OUT params in MS SQL is not supported, use result sets
    END
    @{params}=    Create List    Jerry    OUTPUT
    ${param values}    ${result sets}=    Call Stored Procedure    get_second_name    ${params}
    Length Should Be    ${result sets}    0
    Should Be Equal    ${param values}[1]    Schneider

Procedure Returns Single Value As Result Set
    IF    "${DB_MODULE}" not in ["psycopg2", "psycopg3", "pymssql"]
        Skip    This test is not valid for '${DB_MODULE}'
    END
    @{params}=    Create List    Jerry
    ${param values}    ${result sets}=    Call Stored Procedure    get_second_name    ${params}
    Length Should Be    ${param values}    1
    Should Be Equal    ${param values}[0]    Jerry
    Length Should Be    ${result sets}    1
    ${First result set}=    Set Variable    ${result sets}[0]
    Length Should Be    ${First result set}    1
    Should Be Equal    ${First result set}[0][0]    Schneider

Procedure Returns Result Set Via CURSOR Param
    IF    "${DB_MODULE}" not in ["oracledb", "cx_Oracle"]
        Skip    This test is valid for Oracle only
    END
    @{params}=    Create List    CURSOR
    ${param values}    ${result sets}=    Call Stored Procedure    get_all_second_names    ${params}
    ${length of input params}=    Get Length    ${params}
    Length Should Be    ${param values}    ${length of input params}
    Length Should Be    ${result sets}    1
    ${first result set}=    Set Variable    ${result sets}[0]
    Length Should Be    ${first result set}    2
    Should Be Equal    ${first result set}[0][0]    See
    Should Be Equal    ${first result set}[1][0]    Schneider

Procedure Returns Result Set Without CURSOR Param
    IF    "${DB_MODULE}" in ["oracledb", "cx_Oracle"]
        Skip    This test is not valid for Oracle
    END
    @{params}=    Create List    @{EMPTY}
    ${param values}    ${result sets}=    Call Stored Procedure    get_all_second_names    ${params}
    ${length of input params}=    Get Length    ${params}
    Length Should Be    ${param values}    ${length of input params}
    Length Should Be    ${result sets}    1
    ${first result set}=    Set Variable    ${result sets}[0]
    Length Should Be    ${first result set}    2
    Should Be Equal    ${first result set}[0][0]    See
    Should Be Equal    ${first result set}[1][0]    Schneider

Procedure Returns Multiple Result Sets
    IF    "${DB_MODULE}" in ["oracledb", "cx_Oracle", "psycopg2", "psycopg3"]
        @{params}=    Create List    CURSOR    CURSOR
    ELSE IF    "${DB_MODULE}" in ["pymysql", "pymssql"]
        @{params}=    Create List    @{EMPTY}
    END
    ${param values}    ${result sets}=    Call Stored Procedure    get_all_first_and_second_names    ${params}
    ${length of input params}=    Get Length    ${params}
    Length Should Be    ${param values}    ${length of input params}
    Length Should Be    ${result sets}    2
    ${first result set}=    Set Variable    ${result sets}[0]
    Should Be Equal    ${first result set}[0][0]    Franz Allan
    Should Be Equal    ${first result set}[1][0]    Jerry
    ${second result set}=    Set Variable    ${result sets}[1]
    Should Be Equal    ${second result set}[0][0]    See
    Should Be Equal    ${second result set}[1][0]    Schneider


*** Keywords ***
Create And Fill Tables And Stored Procedures
    Create Person Table And Insert Data
    IF    "${DB_MODULE}" in ["oracledb", "cx_Oracle"]
        Execute SQL Script    ${CURDIR}/../../resources/create_stored_procedures_oracle.sql
    ELSE IF    "${DB_MODULE}" in ["pymysql"]
        Execute SQL Script    ${CURDIR}/../../resources/create_stored_procedure_mysql.sql
    ELSE IF    "${DB_MODULE}" in ["psycopg2", "psycopg3"]
        Execute SQL Script    ${CURDIR}/../../resources/create_stored_procedure_postgres.sql
    ELSE IF    "${DB_MODULE}" in ["pymssql"]
        Execute SQL Script    ${CURDIR}/../../resources/create_stored_procedure_mssql.sql
    ELSE
        Skip    Don't know how to create stored procedures for '${DB_MODULE}'
    END
