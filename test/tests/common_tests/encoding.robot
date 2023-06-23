*** Settings ***
Documentation       Different non ASCII characters work fine

Resource            ../../resources/common.resource

Suite Setup         Connect To DB
Suite Teardown      Disconnect From Database
Test Setup          Create Person Table
Test Teardown       Drop Tables Person And Foobar


*** Test Cases ***
Non ASCII Characters In Values
    Execute Sql String    INSERT INTO person VALUES(1,'Jürgen','Gernegroß')
    ${results}=    Query
    ...    SELECT LAST_NAME FROM person WHERE FIRST_NAME='Jürgen'
    Should Be Equal    ${results}[0][0]    Gernegroß

Read SQL Script Files As UTF8
    [Documentation]    If the SQL script file contains non ASCII characters and saved in UTF8 encoding,
    ...    Pytho might have an issue opening this file on Windows, as it doesn't use UTF8 by default.
    ...    In this case you the library should excplicitely set the UTF8 encoding when opening the script file.
    ...    https://dev.to/methane/python-use-utf-8-mode-on-windows-212i
    Execute Sql Script    ${CURDIR}/../../resources/insert_data_in_person_table_utf8.sql
    ${results}=    Query
    ...    SELECT LAST_NAME FROM person WHERE FIRST_NAME='Jürgen'
    Should Be Equal    ${results}[0][0]    Gernegroß