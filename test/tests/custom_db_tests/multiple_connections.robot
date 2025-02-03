*** Settings ***
Documentation       Connections to two different databases can be handled separately.
...                 These tests require two databases running in parallel.

Resource            ../../resources/common.resource

Suite Setup         Connect To All Databases
Suite Teardown      Disconnect From All Databases
Test Setup          Create Tables
Test Teardown       Drop Tables


*** Variables ***
${Table_1}      table_1
${Table_2}      table_2

${Alias_1}      first
${Alias_2}      second


*** Test Cases ***
First Table Was Created In First Database Only
    Table Must Exist    ${Table_1}    alias=${Alias_1}
    Run Keyword And Expect Error    Table '${Table_2}' does not exist in the db
    ...    Table Must Exist    ${Table_2}    alias=${Alias_1}

Second Table Was Created In Second Database Only
    Table Must Exist    ${Table_2}    alias=${Alias_2}
    Run Keyword And Expect Error    Table '${Table_1}' does not exist in the db
    ...    Table Must Exist    ${Table_1}    alias=${Alias_2}

Switching Default Alias
    Switch Database    ${Alias_1}
    Table Must Exist    ${Table_1}
    Run Keyword And Expect Error    Table '${Table_2}' does not exist in the db
    ...    Table Must Exist    ${Table_2}
    Switch Database    ${Alias_2}
    Table Must Exist    ${Table_2}
    Run Keyword And Expect Error    Table '${Table_1}' does not exist in the db
    ...    Table Must Exist    ${Table_1}


*** Keywords ***
Connect To All Databases
    Connect To Database    psycopg2    db    db_user    pass    127.0.0.1    5432
    ...    alias=${Alias_1}
    Connect To Database    pymysql    db    db_user    pass    127.0.0.1    3306
    ...    alias=${Alias_2}

Create Tables
    ${sql_1}=    Catenate
    ...    CREATE TABLE ${Table_1}
    ...    (id integer not null unique, FIRST_NAME varchar(20), LAST_NAME varchar(20))
    ${sql_2}=    Catenate
    ...    CREATE TABLE ${Table_2}
    ...    (id integer not null unique, FIRST_NAME varchar(20), LAST_NAME varchar(20))
    Execute Sql String    ${sql_1}    alias=${Alias_1}
    Execute Sql String    ${sql_2}    alias=${Alias_2}

Drop Tables
    Execute Sql String    DROP TABLE ${Table_1}    alias=${Alias_1}
    Execute Sql String    DROP TABLE ${Table_2}    alias=${Alias_2}
