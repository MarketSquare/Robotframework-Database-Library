*** Settings ***
Documentation       Tests for querying a table with BLOB data type.
...                 The data type naming is DB specific, these tests are designed for Oracle DB only.

Resource            ../../resources/common.resource

Suite Setup         Connect To DB
Suite Teardown      Disconnect From Database
Test Setup          Execute Sql String
...                     CREATE TABLE blob_table (id integer not null unique, data blob)
Test Teardown       Execute Sql String    DROP TABLE blob_table


*** Variables ***
${DB_MODULE}            oracledb
${DB_HOST}              127.0.0.1
${DB_PORT}              1521
${DB_PASS}              pass
${DB_USER}              db_user
${DB_NAME}              db
${ORACLE_LIB_DIR}       ${EMPTY}


*** Test Cases ***
Blob Data Type - Logging Results Causes No Error
    [Documentation]    See https://github.com/MarketSquare/Robotframework-Database-Library/issues/244
    ${binary_data}=    Evaluate    b'abc'
    Execute Sql String    INSERT INTO blob_table VALUES(1, '${binary_data}')
    ${result}=    Query    SELECT data FROM blob_table WHERE id=1
