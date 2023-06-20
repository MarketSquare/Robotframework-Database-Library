*** Settings ***
Documentation       These tests are mostly different from common tests for other database

Resource            ../../resources/common.resource
Library             ExcelLibrary

Suite Setup         Setup testing excel
Suite Teardown      Cleanup testing excel


*** Variables ***
${DBHost}       dummy
${DBName}       ${CURDIR}/Test_Excel.xlsx
${DBPass}       dummy
${DBPort}       80
${DBUser}       dummy


*** Test Cases ***
Create person table
    ${output} =    Execute SQL String    CREATE TABLE person (id integer,first_name varchar(20),last_name varchar(20));
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Execute SQL Script - Insert Data person table
    log to console    ${DBName}
    ${output} =    Execute SQL Script    ${CURDIR}/../../resources/excel_db_test_insertData.sql
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Execute SQL String - Create Table
    ${output} =    Execute SQL String    create table [foobar] ([id] integer, [firstname] varchar(20))
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Check If Exists In DB - Franz Allan
    Check If Exists In Database    SELECT id FROM [person$] WHERE first_name = 'Franz Allan';

Check If Not Exists In DB - Joe
    Check If Not Exists In Database    SELECT id FROM [person$] WHERE first_name = 'Joe';

Verify Row Count is 0
    Row Count is 0    SELECT * FROM [person$] WHERE first_name = 'NotHere';

Verify Row Count is Equal to X
    Row Count is Equal to X    SELECT id FROM [person$];    2

Verify Row Count is Less Than X
    Row Count is Less Than X    SELECT id FROM [person$];    3

Verify Row Count is Greater Than X
    Row Count is Greater Than X    SELECT * FROM [person$];    1

Retrieve Row Count
    ${output} =    Row Count    SELECT id FROM [person$];
    Log    ${output}
    Should Be Equal As Strings    ${output}    2

Retrieve records from person table
    ${output} =    Execute SQL String    SELECT * FROM [person$];
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify person Description
    Comment    Query db for table column descriptions
    @{queryResults} =    Description    select TOP 1 * FROM [person$];
    Log Many    @{queryResults}
    ${output} =    Set Variable    ${queryResults[0]}
    Should Be Equal As Strings    ${output}    ('id', <class 'str'>, None, 255, 255, 0, True)
    ${output} =    Set Variable    ${queryResults[1]}
    Should Be Equal As Strings    ${output}    ('first_name', <class 'str'>, None, 255, 255, 0, True)
    ${output} =    Set Variable    ${queryResults[2]}
    Should Be Equal As Strings    ${output}    ('last_name', <class 'str'>, None, 255, 255, 0, True)
    ${NumColumns} =    Get Length    ${queryResults}
    Should Be Equal As Integers    ${NumColumns}    3

Verify foobar Description
    Comment    Query db for table column descriptions
    @{queryResults} =    Description    SELECT TOP 1 * FROM [foobar$];
    Log Many    @{queryResults}
    ${output} =    Set Variable    ${queryResults[0]}
    Should Be Equal As Strings    ${output}    ('id', <class 'str'>, None, 255, 255, 0, True)
    ${output} =    Set Variable    ${queryResults[1]}
    Should Be Equal As Strings    ${output}    ('firstname', <class 'str'>, None, 255, 255, 0, True)
    ${NumColumns} =    Get Length    ${queryResults}
    Should Be Equal As Integers    ${NumColumns}    2

Verify Query - Row Count person table
    ${output} =    Query    SELECT COUNT(*) FROM [person$];
    Log    ${output}
    Should Be Equal As Integers    ${output}[0][0]    2

Verify Query - Row Count foobar table
    ${output} =    Query    SELECT COUNT(*) FROM foobar;
    Log    ${output}
    Should Be Equal As Integers    ${output}[0][0]    0

Verify Query - Get results as a list of dictionaries
    ${output} =    Query    SELECT * FROM [person$];    \    True
    Log    ${output}
    Should Be Equal As Strings    ${output[0]}[first_name]    Franz Allan
    Should Be Equal As Strings    ${output[1]}[first_name]    Jerry

Verify Execute SQL String - Row Count person table
    ${output} =    Execute SQL String    SELECT COUNT(*) FROM [person$];
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify Execute SQL String - Row Count foobar table
    ${output} =    Execute SQL String    SELECT COUNT(*) FROM [foobar$];
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Insert Data Into Table foobar
    ${output} =    Execute SQL String    INSERT INTO [foobar$] VALUES(1,'Jerry');
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify Query - Row Count foobar table 1 row
    ${output} =    Query    SELECT COUNT(*) FROM [foobar$];
    Log    ${output}
    Should Be Equal As Integers    ${output}[0][0]    1

Add person in first transaction
    ${output} =    Execute SQL String    INSERT INTO [person$] VALUES(101,'Bilbo','Baggins');    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify person in first transaction
    Row Count is Equal to X    SELECT * FROM [person$] WHERE last_name = 'Baggins';    1    True

Add person in second transaction
    ${output} =    Execute SQL String    INSERT INTO [person$] VALUES(102,'Frodo','Baggins');    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify persons in first and second transactions
    Row Count is Equal to X    SELECT * FROM [person$] WHERE last_name = 'Baggins';    2    True

Setup RO access to excel
    Disconnect From Database
    Connect To Database    excel    ${DBName}    ${DBUser}    ${DBPass}    ${DBHost}    ${DBPort}

Check If Exists In RODB - Franz Allan
    Check If Exists In Database    SELECT id FROM [person$] WHERE first_name = 'Franz Allan';

Check If Not Exists In RODB - Joe
    Check If Not Exists In Database    SELECT id FROM [person$] WHERE first_name = 'Joe';

Verify Row Count is 0 RODB
    Row Count is 0    SELECT * FROM [person$] WHERE first_name = 'NotHere';

Verify Row Count is Equal to X RODB
    Row Count is Equal to X    SELECT id FROM [person$];    4

Verify Row Count is Less Than X RODB
    Row Count is Less Than X    SELECT id FROM [person$];    5

Verify Row Count is Greater Than X RODB
    Row Count is Greater Than X    SELECT * FROM [person$];    1

Retrieve Row Count RODB
    ${output} =    Row Count    SELECT id FROM [person$];
    Log    ${output}
    Should Be Equal As Strings    ${output}    4

Retrieve records from person table RODB
    ${output} =    Execute SQL String    SELECT * FROM [person$];
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify person Description RODB
    Comment    Query db for table column descriptions
    @{queryResults} =    Description    select TOP 1 * FROM [person$];
    Log Many    @{queryResults}
    ${output} =    Set Variable    ${queryResults[0]}
    Should Be Equal As Strings    ${output}    ('id', <class 'str'>, None, 255, 255, 0, True)
    ${output} =    Set Variable    ${queryResults[1]}
    Should Be Equal As Strings    ${output}    ('first_name', <class 'str'>, None, 255, 255, 0, True)
    ${output} =    Set Variable    ${queryResults[2]}
    Should Be Equal As Strings    ${output}    ('last_name', <class 'str'>, None, 255, 255, 0, True)
    ${NumColumns} =    Get Length    ${queryResults}
    Should Be Equal As Integers    ${NumColumns}    3

Verify foobar Description RODB
    Comment    Query db for table column descriptions
    @{queryResults} =    Description    SELECT TOP 1 * FROM [foobar$];
    Log Many    @{queryResults}
    ${output} =    Set Variable    ${queryResults[0]}
    Should Be Equal As Strings    ${output}    ('id', <class 'str'>, None, 255, 255, 0, True)
    ${output} =    Set Variable    ${queryResults[1]}
    Should Be Equal As Strings    ${output}    ('firstname', <class 'str'>, None, 255, 255, 0, True)
    ${NumColumns} =    Get Length    ${queryResults}
    Should Be Equal As Integers    ${NumColumns}    2

Verify Query - Row Count person table RODB
    ${output} =    Query    SELECT COUNT(*) FROM [person$];
    Log    ${output}
    Should Be Equal As Integers    ${output}[0][0]    4

Verify Query - Row Count foobar table RODB
    ${output} =    Query    SELECT COUNT(*) FROM [foobar$];
    Log    ${output}
    Should Be Equal As Integers    ${output}[0][0]    1

Verify Query - Get results as a list of dictionaries RODB
    ${output} =    Query    SELECT * FROM [person$];    \    True
    Log    ${output}
    Should Be Equal As Strings    ${output[0]}[first_name]    Franz Allan
    Should Be Equal As Strings    ${output[1]}[first_name]    Jerry

Verify Execute SQL String - Row Count person table RODB
    ${output} =    Execute SQL String    SELECT COUNT(*) FROM [person$];
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify Execute SQL String - Row Count foobar table RODB
    ${output} =    Execute SQL String    SELECT COUNT(*) FROM [foobar$];
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify Query - Row Count foobar table 1 row RODB
    ${output} =    Query    SELECT COUNT(*) FROM [foobar$];
    Log    ${output}
    Should Be Equal As Integers    ${output}[0][0]    1

Setup RW access to excel
    Disconnect From Database
    Connect To Database    excelrw    ${DBName}    ${DBUser}    ${DBPass}    ${DBHost}    ${DBPort}

Drop person and foobar tables
    ${output} =    Execute SQL String    DROP TABLE [person$],[foobar$]
    Log    ${output}
    Should Be Equal As Strings    ${output}    None


*** Keywords ***
Setup testing excel
    Create Excel Document    excel_db
    Save Excel Document    ${DBName}
    Connect To Database    excelrw    ${DBName}    ${DBUser}    ${DBPass}    ${DBHost}    ${DBPort}

Cleanup testing excel
    Disconnect From Database
    Remove File    ${DBName}
