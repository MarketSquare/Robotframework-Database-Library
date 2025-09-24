*** Settings ***
Documentation       Tests which work with the same input params across all databases.

Resource            ../../resources/common.resource

Suite Setup         Connect To DB
Suite Teardown      Disconnect From Database
Test Setup          Create Table And Set Test Variable
Test Teardown       Drop Tables Person And Foobar


*** Variables ***
${Query with vars}      SELECT * FROM \${PERSON_TABLE}
${Script with vars}     ${Script files dir}/select_with_robot_variables.sql

&{Error}
...    psycopg2=*syntax error*$*
...    oracledb=*$*invalid character*
...    pymssql=*Incorrect syntax*$*
...    pymysql=*error*syntax*
...    pyodbc=*error*syntax*
...    ibm_db_dbi=*Invalid SQL syntax*
...    sqlite3=*unrecognized token*$*


*** Test Cases ***
Query
    ${results}=    Run Keyword And Expect Error    ${Error}[${DB_MODULE}]
    ...    Query    ${Query with vars}
    ${results}=    Run Keyword And Expect Error    ${Error}[${DB_MODULE}]
    ...    Query    ${Query with vars}    replace_robot_variables=False
    Query    ${Query with vars}    replace_robot_variables=True

SQL String
    Run Keyword And Expect Error    ${Error}[${DB_MODULE}]
    ...    Execute Sql String    ${Query with vars}
    Run Keyword And Expect Error    ${Error}[${DB_MODULE}]
    ...    Execute Sql String    ${Query with vars}    replace_robot_variables=False
    Execute Sql String    ${Query with vars}    replace_robot_variables=True

SQL Script
    Run Keyword And Expect Error    ${Error}[${DB_MODULE}]
    ...    Execute Sql Script    ${Script with vars}
    Run Keyword And Expect Error    ${Error}[${DB_MODULE}]
    ...    Execute Sql Script    ${Script with vars}    replace_robot_variables=False
    Execute Sql Script    ${Script with vars}    replace_robot_variables=True

Row Count
    ${result}=    Run Keyword And Expect Error    ${Error}[${DB_MODULE}]
    ...    Row Count    ${Query with vars}
    ${result}=    Run Keyword And Expect Error    ${Error}[${DB_MODULE}]
    ...    Row Count    ${Query with vars}    replace_robot_variables=False
    ${result}=    Row Count    ${Query with vars}    replace_robot_variables=True

Description
    ${result}=    Run Keyword And Expect Error    ${Error}[${DB_MODULE}]
    ...    Description    ${Query with vars}
    ${result}=    Run Keyword And Expect Error    ${Error}[${DB_MODULE}]
    ...    Description    ${Query with vars}    replace_robot_variables=False
    ${result}=    Description    ${Query with vars}    replace_robot_variables=True

Check Query Result
    Run Keyword And Expect Error    ${Error}[${DB_MODULE}]
    ...    Check Query Result    ${Query with vars}    contains    Franz Allan    col=1
    Run Keyword And Expect Error
    ...    ${Error}[${DB_MODULE}]
    ...    Check Query Result
    ...    ${Query with vars}
    ...    contains
    ...    Franz Allan
    ...    col=1
    ...    replace_robot_variables=False
    Check Query Result    ${Query with vars}    contains    Franz Allan    col=1    replace_robot_variables=True

Check Row Count
    Run Keyword And Expect Error    ${Error}[${DB_MODULE}]
    ...    Check Row Count    ${Query with vars}    ==    2
    Run Keyword And Expect Error    ${Error}[${DB_MODULE}]
    ...    Check Row Count    ${Query with vars}    ==    2    replace_robot_variables=False
    Check Row Count    ${Query with vars}    ==    2    replace_robot_variables=True


*** Keywords ***
Create Table And Set Test Variable
    Create Person Table And Insert Data
    Set Test Variable    ${PERSON_TABLE}    person
