*** Settings ***
Library             DatabaseLibrary
Library             OperatingSystem
Library             Collections

Suite Setup         Connect To Database    teradata    ${DBName}    ${DBUser}    ${DBPass}    ${DBHost}    ${DBPort}
Suite Teardown      Disconnect From Database


*** Variables ***
${DBHost}       192.168.0.231
${DBName}       db
${DBPass}       dbc
${DBPort}       1025
${DBUser}       dbc


*** Test Cases ***
Create person table
    [Tags]    db    smoke
    ${output} =    Execute SQL String
    ...    CREATE TABLE person (id integer not null unique,first_name varchar(20),last_name varchar(20))
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Execute SQL Script - Insert Data person table
    Comment    ${output} =    Execute SQL Script    ./${DBName}_insertData.sql
    ${output} =    Execute SQL Script    ${CURDIR}/my_db_test_insertData.sql
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Create foobar table
    ${output} =    Execute SQL String
    ...    create table foobar (id integer not null primary key, firstname varchar(100) not null unique)
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

Retrieve records from person table
    ${output} =    Execute SQL String    SELECT * FROM person;
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify person Description
    [Tags]    db    smoke
    Comment    Query db for table column descriptions
    @{queryResults} =    Description    SELECT * FROM person SAMPLE 1;
    Log Many    @{queryResults}
    ${output} =    Set Variable    ${queryResults[0]}
    Should Be Equal As Strings    ${output}    ('id', <class 'decimal.Decimal'>, None, 10, 0, None, 0)
    ${output} =    Set Variable    ${queryResults[1]}
    Should Be Equal As Strings    ${output}    ('first_name', <class 'str'>, None, 20, 0, None, 1)
    ${output} =    Set Variable    ${queryResults[2]}
    Should Be Equal As Strings    ${output}    ('last_name', <class 'str'>, None, 20, 0, None, 1)
    ${NumColumns} =    Get Length    ${queryResults}
    Should Be Equal As Integers    ${NumColumns}    3

Verify foobar Description
    [Tags]    db    smoke
    Comment    Query db for table column descriptions
    @{queryResults} =    Description    SELECT * FROM foobar SAMPLE 1;
    Log Many    @{queryResults}
    ${output} =    Set Variable    ${queryResults[0]}
    Should Be Equal As Strings    ${output}    ('id', <class 'decimal.Decimal'>, None, 10, 0, None, 0)
    ${output} =    Set Variable    ${queryResults[1]}
    Should Be Equal As Strings    ${output}    ('firstname', <class 'str'>, None, 100, 0, None, 0)
    ${NumColumns} =    Get Length    ${queryResults}
    Should Be Equal As Integers    ${NumColumns}    2

Verify Query - Row Count person table
    ${output} =    Query    SELECT COUNT(*) FROM person;
    Log    ${output}
    ${val} =    Get from list    ${output}    0
    ${val} =    Convert to list    ${val}
    ${val} =    Get from list    ${val}    0
    Should be equal as Integers    ${val}    2

Verify Query - Row Count foobar table
    ${output} =    Query    SELECT COUNT(*) FROM foobar;
    Log    ${output}
    ${val} =    Get from list    ${output}    0
    ${val} =    Convert to list    ${val}
    ${val} =    Get from list    ${val}    0
    Should be equal as Integers    ${val}    0

Verify Query - Get results as a list of dictionaries
    [Tags]    db    smoke
    ${output} =    Query    SELECT * FROM person;    \    True
    Log    ${output}
    Should Be Equal As Strings    ${output}[0][first_name]    Franz Allan
    Should Be Equal As Strings    ${output}[1][first_name]    Jerry

Verify Execute SQL String - Row Count person table
    ${output} =    Execute SQL String    SELECT COUNT(*) FROM person;
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify Execute SQL String - Row Count foobar table
    ${output} =    Execute SQL String    SELECT COUNT(*) FROM foobar;
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Insert Data Into Table foobar
    ${output} =    Execute SQL String    INSERT INTO foobar VALUES(1,'Jerry');
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify Query - Row Count foobar table 1 row
    ${output} =    Query    SELECT COUNT(*) FROM foobar;
    Log    ${output}
    ${val} =    Get from list    ${output}    0
    ${val} =    Convert to list    ${val}
    ${val} =    Get from list    ${val}    0
    Should be equal as Integers    ${val}    1

Verify Delete All Rows From Table - foobar
    Delete All Rows From Table    foobar
    Comment    Sleep    2s

Verify Query - Row Count foobar table 0 row
    Row Count Is 0    SELECT * FROM foobar;
    Comment    ${output} =    Query    SELECT COUNT(*) FROM foobar;
    Comment    Log    ${output}
    Comment    Should Be Equal As Strings    ${output}    [(0,)]

Drop person table
    ${output} =    Execute SQL String    DROP TABLE person;
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Drop foobar table
    ${output} =    Execute SQL String    DROP TABLE foobar;
    Log    ${output}
    Should Be Equal As Strings    ${output}    None
