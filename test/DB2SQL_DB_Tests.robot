*** Settings ***
Suite Setup       Connect To Database    ibm_db_dbi    ${DB2_DBName}    ${DB2_DBUser}    ${DB2_DBPass}    ${DB2_DBHost}    ${DB2_DBPort}
Suite Teardown    Disconnect From Database
Library           DatabaseLibrary
Library           Collections
Force Tags        optional

*** Variables ***
${DBName}         dbname
${DBUser}         user
${DBPass}         password
${DBHost}         host
${DBPort}         port
${DB2_DBName}     ${DBName}
${DB2_DBUser}     ${DBUser}
${DB2_DBPass}     ${DBPass}
${DB2_DBHost}     ${DBHost}
${DB2_DBPort}     ${DBPort}

*** Test Cases ***
Create person table
    ${output} =    Execute SQL String    CREATE TABLE person (id decimal(10,0),first_name varchar(30),last_name varchar(30));
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Execute SQL Script - Insert Data person table
    Comment    ${output} =    Execute SQL Script    ${CURDIR}/my_db_test_insertData.sql
    ${output} =    Execute SQL Script    ${CURDIR}/my_db_test_insertData.sql
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Execute SQL String - Create Table
    ${output} =    Execute SQL String    create table foobar (id integer , firstname varchar(20) )
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Check If Exists In DB - Franz Allan
    Check If Exists In Database    SELECT id FROM person WHERE first_name = 'Franz Allan';

Check If Not Exists In DB - Joe
    Check If Not Exists In Database    SELECT id FROM person WHERE first_name = 'Joe';

Table Must Exist - person
    Table Must Exist    person

Verify Row Count is 0
    Row Count is 0    SELECT * FROM person WHERE first_name = 'NotHere';

Verify Row Count is Equal to X
    Row Count is Equal to X    SELECT id FROM person;    2

Verify Row Count is Less Than X
    Row Count is Less Than X    SELECT id FROM person;    3

Verify Row Count is Greater Than X
    Row Count is Greater Than X    SELECT * FROM person;    1

Retrieve Row Count
    ${output} =    Row Count    SELECT id FROM person;
    Log    ${output}
    Should Be Equal As Strings    ${output}    2

Verify person Description
    [Tags]    db    smoke
    Comment    Query db for table column descriptions
    @{queryResults} =    Description    SELECT * FROM person fetch first 1 rows only;
    Log Many    @{queryResults}
    ${output} =    Set Variable    ${queryResults[0]}
    Should Be Equal As Strings    ${output[0]}    ID
    ${expected}=    Evaluate    ['DEC', 'NUMERIC', 'DECIMAL', 'NUM']
    Lists Should Be Equal    ${output[1].col_types}    ${expected}    ignore_order=True
    Should Be Equal As Strings    ${output[2:]}    [12, 12, 10, 0, True]
    ${output} =    Set Variable    ${queryResults[1]}
    Should Be Equal As Strings    ${output[0]}    FIRST_NAME
    ${expected}=    Evaluate    ['VARCHAR', 'CHARACTER VARYING', 'STRING', 'CHARACTER', 'CHAR', 'CHAR VARYING']
    Lists Should Be Equal    ${output[1].col_types}    ${expected}    ignore_order=True
    Should Be Equal As Strings    ${output[2:]}    [30, 30, 30, 0, True]
    ${output} =    Set Variable    ${queryResults[2]}
    Should Be Equal As Strings    ${output[0]}    LAST_NAME
    ${expected}=    Evaluate    ['CHAR', 'CHAR VARYING', 'VARCHAR', 'CHARACTER VARYING', 'CHARACTER', 'STRING']
    Lists Should Be Equal    ${output[1].col_types}    ${expected}    ignore_order=True
    Should Be Equal As Strings    ${output[2:]}    [30, 30, 30, 0, True]
    ${NumColumns} =    Get Length    ${queryResults}
    Should Be Equal As Integers    ${NumColumns}    3

Verify Query - Row Count person table
    ${output} =    Query    SELECT COUNT(*) FROM person;
    Log    ${output}
    Should Be Equal As Strings    ${output}    [(2,)]

Verify Query - Row Count foobar table
    ${output} =    Query    SELECT COUNT(*) FROM foobar;
    Log    ${output}
    Should Be Equal As Strings    ${output}    [(0,)]

Verify Query - Get results as a list of dictionaries
    [Tags]    db    smoke
    ${output} =    Query    SELECT * FROM person;    \    True
    Log    ${output}
    Should Be Equal As Strings    ${output[0]['FIRST_NAME']}    Franz Allan
    Should Be Equal As Strings    ${output[1]['FIRST_NAME']}    Jerry

Insert Data Into Table foobar
    ${output} =    Execute SQL String    INSERT INTO foobar VALUES(1,'Jerry');
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify Query - Row Count foobar table 1 row
    ${output} =    Query    SELECT COUNT(*) FROM foobar;
    Log    ${output}
    Should Be Equal As Strings    ${output}    [(1,)]

Verify Delete All Rows From Table - foobar
    Delete All Rows From Table    foobar

Verify Query - Row Count foobar table 0 row
    Row Count Is 0    SELECT * FROM foobar;

Drop person and foobar table
    Execute SQL String    DROP TABLE person;
    Execute SQL String    DROP TABLE foobar;

Disconnect from all databases
    Disconnect From All Databases
