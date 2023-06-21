*** Settings ***
Library           DatabaseLibrary
Library           OperatingSystem

*** Variables ***
${DBName}         my_db_test

*** Test Cases ***
Remove old DB if exists
    [Tags]    db    smoke
    ${Status}    ${value} =    Run Keyword And Ignore Error    File Should Not Exist    ./${DBName}.db
    Run Keyword If    "${Status}" == "FAIL"    Run Keyword And Ignore Error    Remove File    ./${DBName}.db
    File Should Not Exist    ./${DBName}.db
    Comment    Sleep    1s

Connect to SQLiteDB
    [Tags]    db    smoke
    Comment    Connect To Database Using Custom Params sqlite3 database='path_to_dbfile\dbname.db'
    Connect To Database Using Custom Params    sqlite3    database="./${DBName}.db", isolation_level=None

Create person table
    [Tags]    db    smoke
    ${output} =    Execute SQL String    CREATE TABLE person (id integer unique,first_name varchar,last_name varchar);
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Execute SQL Script - Insert Data person table
    [Tags]    db    smoke
    ${output} =    Execute SQL Script    ./${DBName}_insertData.sql
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Execute SQL String - Create Table
    [Tags]    db    smoke
    ${output} =    Execute SQL String    create table foobar (id integer primary key, firstname varchar unique)
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Check If Exists In DB - Franz Allan
    [Tags]    db    smoke
    Check If Exists In Database    SELECT id FROM person WHERE first_name = 'Franz Allan';

Check If Exists In DB Fails
    [Tags]    db    smoke
    ${expected_error} =    Catenate
    ...    Expected to have have at least one row from 'SELECT id FROM person WHERE first_name = 'Joe';'
    ...    but got 0 rows.
    Run Keyword And Expect Error    ${expected_error}    Check If Exists In Database
    ...    SELECT id FROM person WHERE first_name = 'Joe';

Check If Exists In DB Fails With Message
    [Tags]    db    smoke
    Run Keyword And Expect Error    my error message    Check If Exists In Database
    ...    SELECT id FROM person WHERE first_name = 'Joe';    msg=my error message

Check If Not Exists In DB - Joe
    [Tags]    db    smoke
    Check If Not Exists In Database    SELECT id FROM person WHERE first_name = 'Joe';

Check If Not Exists In DB Fails
    [Tags]    db    smoke
    ${expected_error} =    Catenate
    ...    Expected to have have no rows from 'SELECT id FROM person WHERE first_name = 'Franz Allan';'
    ...    but got some rows : [(1,)*
    Run Keyword And Expect Error    ${expected_error}    Check If Not Exists In Database
    ...    SELECT id FROM person WHERE first_name = 'Franz Allan';

Check If Not Exists In DB Fails With Message
    [Tags]    db    smoke
    Run Keyword And Expect Error    my error message    Check If Not Exists In Database
    ...    SELECT id FROM person WHERE first_name = 'Franz Allan';    msg=my error message

Table Must Exist - person
    [Tags]    db    smoke
    Table Must Exist    person

Table Must Exist Fails
    [Tags]    db    smoke
    Run Keyword And Expect Error    Table 'nonexistent' does not exist in the db
    ...    Table Must Exist    nonexistent

Table Must Exist Fails With Message
    [Tags]    db    smoke
    Run Keyword And Expect Error    my error message
    ...    Table Must Exist    nonexistent    msg=my error message

Verify Row Count Is 0
    [Tags]    db    smoke
    Row Count Is 0    SELECT * FROM person WHERE first_name = 'NotHere';

Verify Row Count Is 0 Fails
    [Tags]    db    smoke
    ${expected_error} =    Catenate
    ...    Expected zero rows to be returned from 'SELECT * FROM person WHERE first_name = 'Franz Allan';'
    ...    but got rows back. Number of rows returned was 1
    Run Keyword And Expect Error    ${expected_error}    Row Count Is 0
    ...    SELECT * FROM person WHERE first_name = 'Franz Allan';

Verify Row Count Is 0 Fails With Message
    [Tags]    db    smoke
    Run Keyword And Expect Error    my error message    Row Count Is 0
    ...    SELECT * FROM person WHERE first_name = 'Franz Allan';    msg=my error message

Verify Row Count Is Equal To X
    [Tags]    db    smoke
    Row Count Is Equal To X    SELECT id FROM person;    2

Verify Row Count Is Equal To X Fails
    [Tags]    db    smoke
    ${expected_error} =    Catenate
    ...    Expected same number of rows to be returned from 'SELECT id FROM person;'
    ...    than the returned rows of 2
    Run Keyword And Expect Error    ${expected_error}
    ...    Row Count Is Equal To X    SELECT id FROM person;    3

Verify Row Count Is Equal To X Fails With Message
    [Tags]    db    smoke
    Run Keyword And Expect Error    my error message    Row Count Is Equal To X
    ...    SELECT id FROM person;    3    msg=my error message

Verify Row Count Is Less Than X
    [Tags]    db    smoke
    Row Count Is Less Than X    SELECT id FROM person;    3

Verify Row Count Is Less Than X Fails
    [Tags]    db    smoke
    ${expected_error} =    Catenate
    ...    Expected less rows to be returned from 'SELECT id FROM person;'
    ...    than the returned rows of 2
    Run Keyword And Expect Error    ${expected_error}    Row Count Is Less Than X
    ...    SELECT id FROM person;    2

Verify Row Count Is Less Than X Fails With Message
    [Tags]    db    smoke
    Run Keyword And Expect Error    my error message    Row Count Is Less Than X
    ...    SELECT id FROM person;    2    msg=my error message

Verify Row Count Is Greater Than X
    [Tags]    db    smoke
    Row Count Is Greater Than X    SELECT * FROM person;    1

Verify Row Count Is Greater Than X Fails
    [Tags]    db    smoke
    ${expected_error} =    Catenate
    ...    Expected more rows to be returned from 'SELECT * FROM person;'
    ...    than the returned rows of 2
    Run Keyword And Expect Error    ${expected_error}
    ...    Row Count Is Greater Than X    SELECT * FROM person;    3

Verify Row Count Is Greater Than X Fails With Message
    [Tags]    db    smoke
    Run Keyword And Expect Error    my error message    Row Count Is Greater Than X
    ...    SELECT * FROM person;    3    msg=my error message

Retrieve Row Count
    [Tags]    db    smoke
    ${output} =    Row Count    SELECT id FROM person;
    Log    ${output}
    Should Be Equal As Strings    ${output}    2

Retrieve records from person table
    [Tags]    db    smoke
    ${output} =    Execute SQL String    SELECT * FROM person;
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify person Description
    [Tags]    db    smoke
    Comment    Query db for table column descriptions
    @{queryResults} =    Description    SELECT * FROM person LIMIT 1;
    Log Many    @{queryResults}
    ${output} =    Set Variable    ${queryResults[0]}
    Should Be Equal As Strings    ${output}    ('id', None, None, None, None, None, None)
    ${output} =    Set Variable    ${queryResults[1]}
    Should Be Equal As Strings    ${output}    ('first_name', None, None, None, None, None, None)
    ${output} =    Set Variable    ${queryResults[2]}
    Should Be Equal As Strings    ${output}    ('last_name', None, None, None, None, None, None)
    ${NumColumns} =    Get Length    ${queryResults}
    Should Be Equal As Integers    ${NumColumns}    3

Verify foobar Description
    [Tags]    db    smoke
    Comment    Query db for table column descriptions
    @{queryResults} =    Description    SELECT * FROM foobar LIMIT 1;
    Log Many    @{queryResults}
    ${output} =    Set Variable    ${queryResults[0]}
    Should Be Equal As Strings    ${output}    ('id', None, None, None, None, None, None)
    ${output} =    Set Variable    ${queryResults[1]}
    Should Be Equal As Strings    ${output}    ('firstname', None, None, None, None, None, None)
    ${NumColumns} =    Get Length    ${queryResults}
    Should Be Equal As Integers    ${NumColumns}    2

Verify Query - Row Count person table
    [Tags]    db    smoke
    ${output} =    Query    SELECT COUNT(*) FROM person;
    Log    ${output}
    Should Be Equal As Strings    ${output}    [(2,)]

Verify Query - Row Count foobar table
    [Tags]    db    smoke
    ${output} =    Query    SELECT COUNT(*) FROM foobar;
    Log    ${output}
    Should Be Equal As Strings    ${output}    [(0,)]

Verify Query - Get results as a list of dictionaries
    [Tags]    db    smoke
    ${output} =    Query    SELECT * FROM person;    \    True
    Log    ${output}
    Should Be Equal As Strings    ${output}[0][first_name]    Franz Allan
    Should Be Equal As Strings    ${output}[1][first_name]    Jerry

Verify Execute SQL String - Row Count person table
    [Tags]    db    smoke
    ${output} =    Execute SQL String    SELECT COUNT(*) FROM person;
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify Execute SQL String - Row Count foobar table
    [Tags]    db    smoke
    ${output} =    Execute SQL String    SELECT COUNT(*) FROM foobar;
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Insert Data Into Table foobar
    [Tags]    db    smoke
    ${output} =    Execute SQL String    INSERT INTO foobar VALUES(1,'Jerry');
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify Query - Row Count foobar table 1 row
    [Tags]    db    smoke
    ${output} =    Query    SELECT COUNT(*) FROM foobar;
    Log    ${output}
    Should Be Equal As Strings    ${output}    [(1,)]

Verify Delete All Rows From Table - foobar
    [Tags]    db    smoke
    Delete All Rows From Table    foobar
    Comment    Sleep    2s

Verify Query - Row Count foobar table 0 row
    [Tags]    db    smoke
    Row Count Is 0    SELECT * FROM foobar;

Begin first transaction
    [Tags]    db    smoke
    ${output} =    Execute SQL String    SAVEPOINT first    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Add person in first transaction
    [Tags]    db    smoke
    ${output} =    Execute SQL String    INSERT INTO person VALUES(101,'Bilbo','Baggins');    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify person in first transaction
    [Tags]    db    smoke
    Row Count Is Equal To X    SELECT * FROM person WHERE last_name = 'Baggins';    1    True

Begin second transaction
    [Tags]    db    smoke
    ${output} =    Execute SQL String    SAVEPOINT second    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Add person in second transaction
    [Tags]    db    smoke
    ${output} =    Execute SQL String    INSERT INTO person VALUES(102,'Frodo','Baggins');    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify persons in first and second transactions
    [Tags]    db    smoke
    Row Count Is Equal To X    SELECT * FROM person WHERE last_name = 'Baggins';    2    True

Rollback second transaction
    [Tags]    db    smoke
    ${output} =    Execute SQL String    ROLLBACK TO SAVEPOINT second    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify second transaction rollback
    [Tags]    db    smoke
    Row Count Is Equal To X    SELECT * FROM person WHERE last_name = 'Baggins';    1    True

Rollback first transaction
    [Tags]    db    smoke
    ${output} =    Execute SQL String    ROLLBACK TO SAVEPOINT first    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify first transaction rollback
    [Tags]    db    smoke
    Row Count Is 0    SELECT * FROM person WHERE last_name = 'Baggins';    True

Drop person and foobar tables
    [Tags]    db    smoke
    ${output} =    Execute SQL String    DROP TABLE IF EXISTS person;
    Log    ${output}
    Should Be Equal As Strings    ${output}    None
    ${output} =    Execute SQL String    DROP TABLE IF EXISTS foobar;
    Log    ${output}
    Should Be Equal As Strings    ${output}    None
