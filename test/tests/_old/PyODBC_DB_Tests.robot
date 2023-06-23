*** Settings ***
Suite Setup       Connect To Database    ${DBModule}    ${DBName}    ${DBUser}    ${DBPass}    dbHost=${DBHost}    dbPort=${DBPort}    dbCharset=${DBCharset}    dbDriver=${dbDriver}
Suite Teardown    Disconnect From Database
Library           DatabaseLibrary
Library           Collections
Library           OperatingSystem

*** Variables ***
${DBModule}       pyodbc
${DBHost}         ${EMPTY}
${DBName}         ${EMPTY}
${DBPass}         ${EMPTY}
${DBPort}         ${EMPTY}
${DBUser}         ${EMPTY}
${DBCharset}      ${None}
#${dbDriver}       ${EMPTY}

*** Test Cases ***
Create person table
    ${output} =    Execute SQL String    CREATE TABLE person (id integer unique, first_name varchar(20), last_name varchar(20));
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Execute SQL Script - Insert Data person table
    ${output} =    Execute SQL Script    ./my_db_test_insertData.sql
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Execute SQL String - Create Table
    ${output} =    Execute SQL String    create table foobar (id integer primary key, firstname varchar(20) unique)
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
    Comment    Query db for table column descriptions
    @{queryResults} =    Description    SELECT * FROM person LIMIT 1;
    Log Many    @{queryResults}
    ${output} =    Set Variable    ${queryResults[0]}
    Should Be Equal As Strings    ${output}    ('id', <class 'int'>, None, 10, 10, 0, True)
    ${output} =    Set Variable    ${queryResults[1]}
    Should Be Equal As Strings    ${output}    ('first_name', <class 'str'>, None, 20, 20, 0, True)
    ${output} =    Set Variable    ${queryResults[2]}
    Should Be Equal As Strings    ${output}    ('last_name', <class 'str'>, None, 20, 20, 0, True)
    ${NumColumns} =    Get Length    ${queryResults}
    Should Be Equal As Integers    ${NumColumns}    3

Verify foobar Description
    Comment    Query db for table column descriptions
    @{queryResults} =    Description    SELECT * FROM foobar LIMIT 1;
    Log Many    @{queryResults}
    ${output} =    Set Variable    ${queryResults[0]}
    Should Be Equal As Strings    ${output}    ('id', <class 'int'>, None, 10, 10, 0, False)
    ${output} =    Set Variable    ${queryResults[1]}
    Should Be Equal As Strings    ${output}    ('firstname', <class 'str'>, None, 20, 20, 0, True)
    ${NumColumns} =    Get Length    ${queryResults}
    Should Be Equal As Integers    ${NumColumns}    2

Verify Query - Row Count person table
    ${output} =    Query    SELECT COUNT(*) FROM person;
    Log    ${output}
    Should Be Equal As Strings    ${output}    [(2,)]

Verify Query - Row Count foobar table
    ${output} =    Query    SELECT COUNT(*) FROM foobar;
    Log    ${output}
    Should Be Equal As Strings    ${output}    [(0,)]

Verify Query - Get results as a list of dictionaries
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
    Should Be Equal As Strings    ${output}    [(1,)]

Verify Delete All Rows From Table - foobar
    Delete All Rows From Table    foobar
    Comment    Sleep    2s

Verify Query - Row Count foobar table 0 row
    Row Count Is 0    SELECT * FROM foobar;

Begin first transaction
    ${output} =    Execute SQL String    SAVEPOINT first    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Add person in first transaction
    ${output} =    Execute SQL String    INSERT INTO person VALUES(101,'Bilbo','Baggins');    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify person in first transaction
    Row Count is Equal to X    SELECT * FROM person WHERE last_name = 'Baggins';    1    True

Begin second transaction
    ${output} =    Execute SQL String    SAVEPOINT second    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Add person in second transaction
    ${output} =    Execute SQL String    INSERT INTO person VALUES(102,'Frodo','Baggins');    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify persons in first and second transactions
    Row Count is Equal to X    SELECT * FROM person WHERE last_name = 'Baggins';    2    True

Rollback second transaction
    ${output} =    Execute SQL String    ROLLBACK TO second    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify second transaction rollback
    Row Count is Equal to X    SELECT * FROM person WHERE last_name = 'Baggins';    1    True

Rollback first transaction
    ${output} =    Execute SQL String    ROLLBACK TO first    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify first transaction rollback
    Row Count is 0    SELECT * FROM person WHERE last_name = 'Baggins';    True

Drop person and foobar tables
    ${output} =    Execute SQL String    DROP TABLE IF EXISTS person;
    Log    ${output}
    Should Be Equal As Strings    ${output}    None
    ${output} =    Execute SQL String    DROP TABLE IF EXISTS foobar;
    Log    ${output}
    Should Be Equal As Strings    ${output}    None
