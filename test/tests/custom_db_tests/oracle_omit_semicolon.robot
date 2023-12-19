*** Settings ***
Documentation    Tests for the parameter _omitTrailingSemicolon_ in the keyword
...    _Execute SQL String_ - special for the issue #184:
...    https://github.com/MarketSquare/Robotframework-Database-Library/issues/184
...    The _PLSQL BLOCK_ is most likely valid for Oracle DB only.

Resource            ../../resources/common.resource
Suite Setup         Connect To DB
Suite Teardown      Disconnect From Database
Test Setup          Create Person Table And Insert Data
Test Teardown       Drop Tables Person And Foobar


*** Variables ***
${NORMAL QUERY}    SELECT * FROM person;
${PLSQL BLOCK}    DECLARE ERRCODE NUMBER; ERRMSG VARCHAR2(200); BEGIN DBMS_OUTPUT.PUT_LINE('Hello!'); END;


*** Test Cases ***
Explicitely Omit Semicolon
    [Documentation]    Check if it works for Oracle - explicitely omitting the semicolon
    ...    is equal to the default behaviour, otherwise oracle_db throws an error
    Execute Sql String    ${NORMAL QUERY}    omitTrailingSemicolon=True

Explicitely Dont't Omit Semicolon
    [Documentation]    Check if it works for Oracle - it throws an error without a semicolon
    Execute Sql String    ${PLSQL BLOCK}    omitTrailingSemicolon=False
