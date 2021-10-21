*** Settings ***
Library           DatabaseLibrary
Library           OperatingSystem
Force Tags        main    db    smoke

*** Variables ***
${DBName1}        my_db_test1
${DBName2}        my_db_test2

*** Keywords ***
Remove DB file if exists
    [Arguments]    ${DB_FILE}
    Run Keyword And Ignore Error    Remove File    ${DB_FILE}
    File Should Not Exist    ${DB_FILE}
    Comment    Sleep    1s

*** Test Cases ***
Remove old DB if exists
    Remove DB file if exists    ${CURDIR}/${DBName1}.db
    Remove DB file if exists    ${CURDIR}/${DBName2}.db

Connect to SQLiteDB
    Comment    Connect To Database Using Custom Params sqlite3 database='path_to_dbfile\dbname.db'
    Connect To Database Using Custom Params    sqlite3    database="${CURDIR}/${DBName1}.db", isolation_level=None    alias=db1
    Connect To Database Using Custom Params    sqlite3    database="${CURDIR}/${DBName2}.db", isolation_level=None    alias=db2

Create person table
    ${output} =    Execute SQL String    CREATE TABLE person (id integer unique,first_name varchar,last_name varchar);    alias=db2
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Create foobar table
    ${output} =    Execute SQL String    create table foobar (id integer primary key, firstname varchar unique)    alias=db1
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Table Must Exist - person
    Table Must Exist    person    alias=db2

Table Shouldn't Exist - person
    Run Keyword And Expect Error    Table 'person' does not exist in the db    Table Must Exist    person    alias=db1

Table Shouldn't Exist - foobar
    Run Keyword And Expect Error    Table 'foobar' does not exist in the db    Table Must Exist    foobar    alias=db2

Switch database without alias
    Switch Database    db2
    Table Must Exist    person
    Run Keyword And Expect Error    Table 'foobar' does not exist in the db    Table Must Exist    foobar

Disconnect from database db1
    Disconnect From Database    alias=db1

Disconnect from all databases
    Disconnect From All Databases
