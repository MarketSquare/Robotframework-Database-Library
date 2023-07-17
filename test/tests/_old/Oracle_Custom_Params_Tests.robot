*** Settings ***
Library             DatabaseLibrary
Library             Collections

Suite Setup         Connect To DB
Suite Teardown      Disconnect From Database
Test Setup          Create Person Table And Insert Data
Test Teardown       Drop Tables


*** Variables ***
${DBHost}       127.0.0.1
${DBName}       db
${DBPass}       pass
${DBPort}       1521
${DBUser}       db_user


*** Test Cases ***
Create Person Table
    [Setup]    Log    No setup for this test
    ${output} =    Create Person Table
    Should Be Equal As Strings    ${output}    None

Execute SQL Script - Insert Data person table
    [Tags]    db    smoke
    [Setup]    Create Person Table
    ${output} =    Execute SQL Script    ${CURDIR}/my_db_test_insertData.sql
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Execute SQL String - Create Table
    [Tags]    db    smoke
    [Setup]    Log    No setup for this test
    ${output} =    Create Foobar Table
    Should Be Equal As Strings    ${output}    None

Check If Exists In DB - Franz Allan
    [Tags]    db    smoke
    Check If Exists In Database    SELECT id FROM person WHERE first_name = 'Franz Allan'

Check If Not Exists In DB - Joe
    [Tags]    db    smoke
    Check If Not Exists In Database    SELECT id FROM person WHERE first_name = 'Joe'

Table Must Exist - person
    [Tags]    db    smoke
    Table Must Exist    person

Verify Row Count is 0
    [Tags]    db    smoke
    Row Count is 0    SELECT * FROM person WHERE first_name = 'NotHere'

Verify Row Count is Equal to X
    [Tags]    db    smoke
    Row Count is Equal to X    SELECT id FROM person    2

Verify Row Count is Less Than X
    [Tags]    db    smoke
    Row Count is Less Than X    SELECT id FROM person    3

Verify Row Count is Greater Than X
    [Tags]    db    smoke
    Row Count is Greater Than X    SELECT * FROM person    1

Retrieve Row Count
    [Tags]    db    smoke
    ${output} =    Row Count    SELECT id FROM person
    Log    ${output}
    Should Be Equal As Strings    ${output}    2

Retrieve records from person table
    [Tags]    db    smoke
    ${output} =    Execute SQL String    SELECT * FROM person
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify person Description
    [Tags]    db    smoke
    Comment    Query db for table column descriptions
    @{queryResults} =    Description    SELECT * FROM person FETCH FIRST 1 ROWS ONLY
    Log Many    @{queryResults}
    ${output} =    Set Variable    ${queryResults[0]}
    Should Be Equal As Strings    ${output}    ('ID', <DbType DB_TYPE_NUMBER>, 39, None, 38, 0, False)
    ${output} =    Set Variable    ${queryResults[1]}
    Should Be Equal As Strings    ${output}    ('FIRST_NAME', <DbType DB_TYPE_VARCHAR>, 20, 20, None, None, False)
    ${output} =    Set Variable    ${queryResults[2]}
    Should Be Equal As Strings    ${output}    ('LAST_NAME', <DbType DB_TYPE_VARCHAR>, 20, 20, None, None, False)
    ${NumColumns} =    Get Length    ${queryResults}
    Should Be Equal As Integers    ${NumColumns}    3

Verify foobar Description
    [Tags]    db    smoke
    [Setup]    Create Foobar Table
    Comment    Query db for table column descriptions
    @{queryResults} =    Description    SELECT * FROM foobar FETCH FIRST 1 ROWS ONLY
    Log Many    @{queryResults}
    ${output} =    Set Variable    ${queryResults[0]}
    Should Be Equal As Strings    ${output}    ('ID', <DbType DB_TYPE_NUMBER>, 39, None, 38, 0, False)
    ${output} =    Set Variable    ${queryResults[1]}
    Should Be Equal As Strings    ${output}    ('FIRST_NAME', <DbType DB_TYPE_VARCHAR>, 20, 20, None, None, False)
    ${NumColumns} =    Get Length    ${queryResults}
    Should Be Equal As Integers    ${NumColumns}    2

Verify Query - Row Count person table
    [Tags]    db    smoke
    ${output} =    Query    SELECT COUNT(*) FROM person
    Log    ${output}
    ${val} =    Get from list    ${output}    0
    ${val} =    Convert to list    ${val}
    ${val} =    Get from list    ${val}    0
    Should be equal as Integers    ${val}    2

Verify Query - Row Count foobar table
    [Tags]    db    smoke
    [Setup]    Create Foobar Table
    ${output} =    Query    SELECT COUNT(*) FROM foobar
    Log    ${output}
    ${val} =    Get from list    ${output}    0
    ${val} =    Convert to list    ${val}
    ${val} =    Get from list    ${val}    0
    Should be equal as Integers    ${val}    0

Verify Query - Get results as a list of dictionaries
    [Tags]    db    smoke
    ${output} =    Query    SELECT * FROM person    \    True
    Log    ${output}
    Should Be Equal As Strings    ${output}[0][FIRST_NAME]    Franz Allan
    Should Be Equal As Strings    ${output}[1][FIRST_NAME]    Jerry

Verify Execute SQL String - Row Count person table
    [Tags]    db    smoke
    ${output} =    Execute SQL String    SELECT COUNT(*) FROM person
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify Execute SQL String - Row Count foobar table
    [Tags]    db    smoke
    [Setup]    Create Foobar Table
    ${output} =    Execute SQL String    SELECT COUNT(*) FROM foobar
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Insert Data Into Table foobar
    [Tags]    db    smoke
    [Setup]    Create Foobar Table
    ${output} =    Execute SQL String    INSERT INTO foobar VALUES(1,'Jerry')
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify Query - Row Count foobar table 1 row
    [Tags]    db    smoke
    [Setup]    Create Foobar Table And Insert Data
    ${output} =    Query    SELECT COUNT(*) FROM foobar
    Log    ${output}
    ${val} =    Get from list    ${output}    0
    ${val} =    Convert to list    ${val}
    ${val} =    Get from list    ${val}    0
    Should be equal as Integers    ${val}    1

Verify Delete All Rows From Table - foobar
    [Tags]    db    smoke
    [Setup]    Create Foobar Table And Insert Data
    Delete All Rows From Table    foobar
    Comment    Sleep    2s

Verify Query - Row Count foobar table 0 row
    [Tags]    db    smoke
    [Setup]    Create Foobar Table And Insert Data
    Delete All Rows From Table    foobar
    Row Count Is 0    SELECT * FROM foobar
    Comment    ${output} =    Query    SELECT COUNT(*) FROM foobar
    Comment    Log    ${output}
    Comment    Should Be Equal As Strings    ${output}    [(0,)]

Transaction
    [Tags]    db    smoke
    [Setup]    Create Person Table
    Begin first transaction
    Add person in first transaction
    Verify person in first transaction
    Begin second transaction
    Add person in second transaction
    Verify persons in first and second transactions
    Rollback second transaction
    Verify second transaction rollback
    Rollback first transaction
    Verify first transaction rollback


*** Keywords ***
Connect To DB
    ${con_str} =    Catenate    SEPARATOR=${EMPTY}
    ...    ${DBUser}/${DBPass}@
    ...    ${DBHost}:${DBPort}/${DBName}
    Connect To Database Using Custom Params    oracledb    "${con_str}"

Create Person Table
    # ${sql} =    Catenate
    # ...    CREATE TABLE person
    # ...    (id INT GENERATED BY DEFAULT AS IDENTITY,
    # ...    first_name varchar2(20) NOT NULL,
    # ...    last_name varchar2(20) NOT NULL,
    # ...    PRIMARY KEY(id))
    ${sql} =    Catenate
    ...    CREATE TABLE person
    ...    (id integer not null unique,first_name varchar(20),last_name varchar(20))
    ${output} =    Execute Sql String    ${sql}
    RETURN    ${output}

Create Person Table And Insert Data
    Create Person Table
    Execute SQL Script    ${CURDIR}/my_db_test_insertData.sql

Create Foobar Table
    ${sql} =    Catenate
    ...    CREATE TABLE foobar
    ...    (id INT GENERATED BY DEFAULT AS IDENTITY,
    ...    first_name varchar2(20) NOT NULL,
    ...    PRIMARY KEY(id))
    ${output} =    Execute Sql String    ${sql}
    RETURN    ${output}

Create Foobar Table And Insert Data
    Create Foobar Table
    Execute SQL String    INSERT INTO foobar VALUES(1,'Jerry')

Begin first transaction
    ${output} =    Execute SQL String    SAVEPOINT first    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Add person in first transaction
    ${output} =    Execute SQL String    INSERT INTO person VALUES(101,'Bilbo','Baggins')    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify person in first transaction
    Row Count is Equal to X    SELECT * FROM person WHERE last_name = 'Baggins'    1    True

Begin second transaction
    ${output} =    Execute SQL String    SAVEPOINT second    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Add person in second transaction
    ${output} =    Execute SQL String    INSERT INTO person VALUES(102,'Frodo','Baggins')    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify persons in first and second transactions
    Row Count is Equal to X    SELECT * FROM person WHERE last_name = 'Baggins'    2    True

Rollback second transaction
    ${output} =    Execute SQL String    ROLLBACK TO SAVEPOINT second    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify second transaction rollback
    Row Count is Equal to X    SELECT * FROM person WHERE last_name = 'Baggins'    1    True

Rollback first transaction
    ${output} =    Execute SQL String    ROLLBACK TO SAVEPOINT first    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify first transaction rollback
    Row Count is 0    SELECT * FROM person WHERE last_name = 'Baggins'    True

Drop Tables
    ${sql} =    Catenate    DROP TABLE IF EXISTS person
    Execute SQL String    ${sql}
    ${sql} =    Catenate    DROP TABLE IF EXISTS foobar
    Execute SQL String    ${sql}
