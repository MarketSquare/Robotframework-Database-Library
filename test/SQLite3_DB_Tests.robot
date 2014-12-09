*** Settings ***
Library           DatabaseLibrary
Library           OperatingSystem

*** Variables ***
${DBName}         my_db_test

*** Test Cases ***
Remove old DB if exists
    Comment    ${Status}    ${value} =    Run Keyword And Ignore Error    File Should Not Exist    /Users/jerry/Desktop/TestCases/TestSQLite3.db
    ${Status}    ${value} =    Run Keyword And Ignore Error    File Should Not Exist    ./${DBName}.db
    Comment    Run Keyword If    "${Status}" == "FAIL"    Run Keyword And Ignore Error    Run    rm -rf $HOME/Desktop/TestCases/TestSQLite3.db
    Run Keyword If    "${Status}" == "FAIL"    Run Keyword And Ignore Error    Run    rm -rf ./${DBName}.db
    Comment    File Should Not Exist    /Users/jerry/Desktop/TestCases/TestSQLite3.db
    File Should Not Exist    ./${DBName}.db
    Comment    Sleep    1s

Connect to SQLiteDB
    Comment    Connect To Database Using Custom Params sqlite3 database='path_to_dbfile\dbname.db'
    Connect To Database Using Custom Params    sqlite3    database="./${DBName}.db"

Create person table
    ${output} =    Execute SQL String    CREATE TABLE person (id integer unique,first_name varchar,last_name varchar);
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Execute SQL Script - Insert Data person table
    ${output} =    Execute SQL Script    ./${DBName}_insertData.sql
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Execute SQL String - Create Table
    ${output} =    Execute SQL String    create table foobar (id integer primary key, firstname varchar unique)
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
    ${output} =    Query    SELECT COUNT(*) FROM person;
    Log    ${output}
    Should Be Equal As Strings    ${output}    [(2,)]

Verify Query - Row Count foobar table
    ${output} =    Query    SELECT COUNT(*) FROM foobar;
    Log    ${output}
    Should Be Equal As Strings    ${output}    [(0,)]

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
    Comment    ${output} =    Query    SELECT COUNT(*) FROM foobar;
    Comment    Log    ${output}
    Comment    Should Be Equal As Strings    ${output}    [(0,)]

Drop person and foobar tables
    ${output} =    Execute SQL String    DROP TABLE IF EXISTS person;
    Log    ${output}
    Should Be Equal As Strings    ${output}    None
    ${output} =    Execute SQL String    DROP TABLE IF EXISTS foobar;
    Log    ${output}
    Should Be Equal As Strings    ${output}    None
