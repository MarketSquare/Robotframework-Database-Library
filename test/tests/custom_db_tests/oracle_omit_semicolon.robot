*** Settings ***
Documentation       Tests for the parameter _omitTrailingSemicolon_ in the keyword
...                 _Execute SQL String_ - special for the issue #184:
...                 https://github.com/MarketSquare/Robotframework-Database-Library/issues/184
...                 The _PLSQL BLOCK_ is most likely valid for Oracle DB only.

Resource            ../../resources/common.resource

Suite Setup         Connect To DB
Suite Teardown      Disconnect From Database
Test Setup          Create Person Table And Insert Data
Test Teardown       Drop Tables Person And Foobar


*** Variables ***
${NORMAL QUERY}             SELECT * FROM person;
${PLSQL BLOCK}              DECLARE ERRCODE NUMBER; ERRMSG VARCHAR2(200); BEGIN DBMS_OUTPUT.PUT_LINE('Hello!'); END;

${ERROR SIMPLE QUERY}       *ORA-03048: SQL reserved word ';' is not syntactically valid following*
${ERROR PLSQL}              *PLS-00103: Encountered the symbol "end-of-file" when expecting one of the following*


*** Test Cases ***
Explicitely Omit Semicolon - Simple Query
    [Documentation]    Check if it works for Oracle - explicitly omitting the semicolon
    ...    is equal to the default behavior
    Execute Sql String    ${NORMAL QUERY}    omit_trailing_semicolon=True

Explicitely Don't Omit Semicolon - Simple Query
    [Documentation]    Check if Oracle throws an error

    Run Keyword And Expect Error    ${ERROR SIMPLE QUERY}
    ...    Execute Sql String    ${NORMAL QUERY}    omit_trailing_semicolon=False

Explicitely Omit Semicolon - PLSQL Block
    [Documentation]    Check if Oracle throws an error
    Run Keyword And Expect Error    ${ERROR PLSQL}
    ...    Execute Sql String    ${PLSQL BLOCK}    omit_trailing_semicolon=True

Explicitely Don't Omit Semicolon - PLSQL Block
    [Documentation]    Should run without errors, because the semicolon is needed
    ...    at the end of the PLSQL block even with Oracle
    Execute Sql String    ${PLSQL BLOCK}    omit_trailing_semicolon=False

Explicitely Omit Semicolon With Keyword - Simple Query
    [Documentation]    Check if it works for Oracle - explicitly omitting the semicolon
    ...    is equal to the default behavior
    Set Omit Trailing Semicolon    True
    Execute Sql String    ${NORMAL QUERY}

Explicitely Don't Omit Semicolon With Keyword - Simple Query
    [Documentation]    Check if Oracle throws an error
    Set Omit Trailing Semicolon    False    
    Run Keyword And Expect Error    ${ERROR SIMPLE QUERY}
    ...    Execute Sql String    ${NORMAL QUERY}

Explicitely Omit Semicolon With Keyword - PLSQL Block
    [Documentation]    Check if Oracle throws an error
    Set Omit Trailing Semicolon    True    
    Run Keyword And Expect Error    ${ERROR PLSQL}
    ...    Execute Sql String    ${PLSQL BLOCK}

Explicitely Don't Omit Semicolon With Keyword - PLSQL Block
    [Documentation]    Should run without errors, because the semicolon is needed
    ...    at the end of the PLSQL block even with Oracle
    Set Omit Trailing Semicolon    False
    Execute Sql String    ${PLSQL BLOCK}
