*** Settings ***
Documentation       Testing the transaction rollback requires savepoints -
...                 setting them is diffferent depending on the database

Resource            ../../resources/common.resource

Suite Setup         Connect To DB
Suite Teardown      Disconnect From Database
Test Setup          Create Person Table
Test Teardown       Drop Tables Person And Foobar


*** Test Cases ***
Transaction
    IF    "${DB_MODULE}" == "teradata"
        Skip    Teradata doesn't support savepoints
    END
    Begin first transaction
    Add person in first transaction
    Verify person in first transaction
    Begin second transaction
    Add person in second transaction
    Verify persons in first and second transactions
    Rollback second transaction
    Verify second transaction rollback
    Rollback first transaction
    Verify first transaction rollback


*** Keywords ***
Begin first transaction
    ${sql}=    Set Variable    SAVEPOINT first
    IF    "${DB_MODULE}" == "ibm_db_dbi"
        ${sql}=    Catenate    ${sql}
        ...    ON ROLLBACK RETAIN CURSORS
    ELSE IF    "${DB_MODULE}" == "pymssql"
        ${sql}=    Set Variable    SAVE TRANSACTION first
    END
    ${output}=    Execute SQL String    ${sql}    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Add person in first transaction
    ${output}=    Execute SQL String    INSERT INTO person VALUES(101,'Bilbo','Baggins')    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify person in first transaction
    Row Count is Equal to X    SELECT * FROM person WHERE LAST_NAME= 'Baggins'    1    True

Begin second transaction
    ${sql}=    Set Variable    SAVEPOINT second
    IF    "${DB_MODULE}" == "ibm_db_dbi"
        ${sql}=    Catenate    ${sql}
        ...    ON ROLLBACK RETAIN CURSORS
    ELSE IF    "${DB_MODULE}" == "pymssql"
        ${sql}=    Set Variable    SAVE TRANSACTION second
    END
    ${output}=    Execute SQL String    ${sql}    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Add person in second transaction
    ${output}=    Execute SQL String    INSERT INTO person VALUES(102,'Frodo','Baggins')    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify persons in first and second transactions
    Row Count is Equal to X    SELECT * FROM person WHERE LAST_NAME= 'Baggins'    2    True

Rollback second transaction
    ${sql}=    Set Variable    ROLLBACK TO SAVEPOINT second
    IF    "${DB_MODULE}" == "pymssql"
        ${sql}=    Set Variable    ROLLBACK TRANSACTION second
    END
    ${output}=    Execute SQL String    ${sql}    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify second transaction rollback
    Row Count is Equal to X    SELECT * FROM person WHERE LAST_NAME= 'Baggins'    1    True

Rollback first transaction
    ${sql}=    Set Variable    ROLLBACK TO SAVEPOINT first
    IF    "${DB_MODULE}" == "pymssql"
        ${sql}=    Set Variable    ROLLBACK TRANSACTION first
    END
    ${output}=    Execute SQL String    ${sql}
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify first transaction rollback
    Row Count is 0    SELECT * FROM person WHERE LAST_NAME= 'Baggins'    True
