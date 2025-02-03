*** Settings ***
Suite Setup       Setup testing excel
Suite Teardown    Cleanup testing excel
Library           DatabaseLibrary
Library           OperatingSystem
Library           ExcelLibrary

*** Variables ***
${DBHost}         dummy
${DBName}         ${EXECDIR}/test/Test_Excel.xls
${DBPass}         dummy
${DBPort}         80
${DBUser}         dummy

*** Test Cases ***
Create person table
    [Tags]    db    smoke
    ${output} =    Execute SQL String    CREATE TABLE person (id integer,first_name varchar(20),last_name varchar(20));
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Execute SQL Script - Insert Data person table
    [Tags]    db    smoke
    log to console  ${DBName}
    Comment    ${output} =    Execute SQL Script    ${EXECDIR}/test/excel_db_test_insertData.sql
    ${output} =    Execute SQL Script    ${EXECDIR}/test/excel_db_test_insertData.sql
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Execute SQL String - Create Table
    [Tags]    db    smoke
    ${output} =    Execute SQL String    create table [foobar] ([id] integer, [firstname] varchar(20))
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Check If Exists In DB - Franz Allan
    [Tags]    db    smoke
    Check If Exists In Database    SELECT id FROM [person$] WHERE first_name = 'Franz Allan';

Check If Not Exists In DB - Joe
    [Tags]    db    smoke
    Check If Not Exists In Database    SELECT id FROM [person$] WHERE first_name = 'Joe';


Verify Row Count is 0
    [Tags]    db    smoke
    Row Count is 0    SELECT * FROM [person$] WHERE first_name = 'NotHere';

Verify Row Count is Equal to X
    [Tags]    db    smoke
    Row Count is Equal to X    SELECT id FROM [person$];    2

Verify Row Count is Less Than X
    [Tags]    db    smoke
    Row Count is Less Than X    SELECT id FROM [person$];    3

Verify Row Count is Greater Than X
    [Tags]    db    smoke
    Row Count is Greater Than X    SELECT * FROM [person$];    1

Retrieve Row Count
    [Tags]    db    smoke
    ${output} =    Row Count    SELECT id FROM [person$];
    Log    ${output}
    Should Be Equal As Strings    ${output}    2

Retrieve records from person table
    [Tags]    db    smoke
    ${output} =    Execute SQL String    SELECT * FROM [person$];
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify person Description
    [Tags]    db    smoke
    Comment    Query db for table column descriptions
    @{queryResults} =    Description    select TOP 1 * FROM [person$];
    Log Many    @{queryResults}
    ${output} =    Set Variable    ${queryResults[0]}
    Should Be Equal As Strings    ${output}    ('id', <type 'str'>, None, 255, 255, 0, True)
    ${output} =    Set Variable    ${queryResults[1]}
    Should Be Equal As Strings    ${output}    ('first_name', <type 'str'>, None, 255, 255, 0, True)
    ${output} =    Set Variable    ${queryResults[2]}
    Should Be Equal As Strings    ${output}    ('last_name', <type 'str'>, None, 255, 255, 0, True)
    ${NumColumns} =    Get Length    ${queryResults}
    Should Be Equal As Integers    ${NumColumns}    3

Verify foobar Description
    [Tags]    db    smoke
    Comment    Query db for table column descriptions
    @{queryResults} =    Description    SELECT TOP 1 * FROM [foobar$];
    Log Many    @{queryResults}
    ${output} =    Set Variable    ${queryResults[0]}
    Should Be Equal As Strings    ${output}    ('id', <type 'str'>, None, 255, 255, 0, True)
    ${output} =    Set Variable    ${queryResults[1]}
    Should Be Equal As Strings    ${output}    ('firstname', <type 'str'>, None, 255, 255, 0, True)
    ${NumColumns} =    Get Length    ${queryResults}
    Should Be Equal As Integers    ${NumColumns}    2

Verify Query - Row Count person table
    [Tags]    db    smoke
    ${output} =    Query    SELECT COUNT(*) FROM [person$];
    Log    ${output}
    Should Be Equal As Strings    ${output}    [(2, )]

Verify Query - Row Count foobar table
    [Tags]    db    smoke
    ${output} =    Query    SELECT COUNT(*) FROM foobar;
    Log    ${output}
    Should Be Equal As Strings    ${output}    [(0, )]

Verify Query - Get results as a list of dictionaries
    [Tags]    db    smoke
    ${output} =    Query    SELECT * FROM [person$];    \    True
    Log    ${output}
    Should Be Equal As Strings    &{output[0]}[first_name]    Franz Allan
    Should Be Equal As Strings    &{output[1]}[first_name]    Jerry

Verify Execute SQL String - Row Count person table
    [Tags]    db    smoke
    ${output} =    Execute SQL String    SELECT COUNT(*) FROM [person$];
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify Execute SQL String - Row Count foobar table
    [Tags]    db    smoke
    ${output} =    Execute SQL String    SELECT COUNT(*) FROM [foobar$];
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Insert Data Into Table foobar
    [Tags]    db    smoke
    ${output} =    Execute SQL String    INSERT INTO [foobar$] VALUES(1,'Jerry');
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify Query - Row Count foobar table 1 row
    [Tags]    db    smoke
    ${output} =    Query    SELECT COUNT(*) FROM [foobar$];
    Log    ${output}
    Should Be Equal As Strings    ${output}    [(1, )]


Add person in first transaction
    [Tags]    db    smoke
    ${output} =    Execute SQL String    INSERT INTO [person$] VALUES(101,'Bilbo','Baggins');    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify person in first transaction
    [Tags]    db    smoke
    Row Count is Equal to X    SELECT * FROM [person$] WHERE last_name = 'Baggins';    1    True

#Begin second transaction
#    [Tags]    db    smoke
#    ${output} =    Execute SQL String    SAVEPOINT second    True
#    Log    ${output}
#    Should Be Equal As Strings    ${output}    None

Add person in second transaction
    [Tags]    db    smoke
    ${output} =    Execute SQL String    INSERT INTO [person$] VALUES(102,'Frodo','Baggins');    True
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify persons in first and second transactions
    [Tags]    db    smoke
    Row Count is Equal to X    SELECT * FROM [person$] WHERE last_name = 'Baggins';    2    True

Setup RO access to excel
    Disconnect From Database
    Connect To Database  excel   ${DBName}    ${DBUser}    ${DBPass}    ${DBHost}    ${DBPort}


Check If Exists In RODB - Franz Allan
    [Tags]    db    smoke
    Check If Exists In Database    SELECT id FROM [person$] WHERE first_name = 'Franz Allan';

Check If Not Exists In RODB - Joe
    [Tags]    db    smoke
    Check If Not Exists In Database    SELECT id FROM [person$] WHERE first_name = 'Joe';


Verify Row Count is 0 RODB
    [Tags]    db    smoke
    Row Count is 0    SELECT * FROM [person$] WHERE first_name = 'NotHere';

Verify Row Count is Equal to X RODB
    [Tags]    db    smoke
    Row Count is Equal to X    SELECT id FROM [person$];    4

Verify Row Count is Less Than X RODB
    [Tags]    db    smoke
    Row Count is Less Than X    SELECT id FROM [person$];    5

Verify Row Count is Greater Than X RODB
    [Tags]    db    smoke
    Row Count is Greater Than X    SELECT * FROM [person$];    1

Retrieve Row Count RODB
    [Tags]    db    smoke
    ${output} =    Row Count    SELECT id FROM [person$];
    Log    ${output}
    Should Be Equal As Strings    ${output}    4

Retrieve records from person table RODB
    [Tags]    db    smoke
    ${output} =    Execute SQL String    SELECT * FROM [person$];
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify person Description RODB
    [Tags]    db    smoke
    Comment    Query db for table column descriptions
    @{queryResults} =    Description    select TOP 1 * FROM [person$];
    Log Many    @{queryResults}
    ${output} =    Set Variable    ${queryResults[0]}
    Should Be Equal As Strings    ${output}    ('id', <type 'str'>, None, 255, 255, 0, True)
    ${output} =    Set Variable    ${queryResults[1]}
    Should Be Equal As Strings    ${output}    ('first_name', <type 'str'>, None, 255, 255, 0, True)
    ${output} =    Set Variable    ${queryResults[2]}
    Should Be Equal As Strings    ${output}    ('last_name', <type 'str'>, None, 255, 255, 0, True)
    ${NumColumns} =    Get Length    ${queryResults}
    Should Be Equal As Integers    ${NumColumns}    3

Verify foobar Description RODB
    [Tags]    db    smoke
    Comment    Query db for table column descriptions
    @{queryResults} =    Description    SELECT TOP 1 * FROM [foobar$];
    Log Many    @{queryResults}
    ${output} =    Set Variable    ${queryResults[0]}
    Should Be Equal As Strings    ${output}    ('id', <type 'str'>, None, 255, 255, 0, True)
    ${output} =    Set Variable    ${queryResults[1]}
    Should Be Equal As Strings    ${output}    ('firstname', <type 'str'>, None, 255, 255, 0, True)
    ${NumColumns} =    Get Length    ${queryResults}
    Should Be Equal As Integers    ${NumColumns}    2

Verify Query - Row Count person table RODB
    [Tags]    db    smoke
    ${output} =    Query    SELECT COUNT(*) FROM [person$];
    Log    ${output}
    Should Be Equal As Strings    ${output}    [(4, )]

Verify Query - Row Count foobar table RODB
    [Tags]    db    smoke
    ${output} =    Query    SELECT COUNT(*) FROM [foobar$];
    Log    ${output}
    Should Be Equal As Strings    ${output}    [(1, )]

Verify Query - Get results as a list of dictionaries RODB
    [Tags]    db    smoke
    ${output} =    Query    SELECT * FROM [person$];    \    True
    Log    ${output}
    Should Be Equal As Strings    &{output[0]}[first_name]    Franz Allan
    Should Be Equal As Strings    &{output[1]}[first_name]    Jerry

Verify Execute SQL String - Row Count person table RODB
    [Tags]    db    smoke
    ${output} =    Execute SQL String    SELECT COUNT(*) FROM [person$];
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify Execute SQL String - Row Count foobar table RODB
    [Tags]    db    smoke
    ${output} =    Execute SQL String    SELECT COUNT(*) FROM [foobar$];
    Log    ${output}
    Should Be Equal As Strings    ${output}    None


Verify Query - Row Count foobar table 1 row RODB
    [Tags]    db    smoke
    ${output} =    Query    SELECT COUNT(*) FROM [foobar$];
    Log    ${output}
    Should Be Equal As Strings    ${output}    [(1, )]

Setup RW access to excel
    Disconnect From Database
    Connect To Database  excelrw   ${DBName}    ${DBUser}    ${DBPass}    ${DBHost}    ${DBPort}

Drop person and foobar tables
    [Tags]    db    smoke
    ${output} =    Execute SQL String    DROP TABLE [person$],[foobar$]
    Log    ${output}
    Should Be Equal As Strings    ${output}    None


*** Keywords ***

Setup testing excel
    Create Excel Document     Test_Excel
    Connect To Database  excelrw   ${DBName}    ${DBUser}    ${DBPass}    ${DBHost}    ${DBPort}

Cleanup testing excel
    Disconnect From Database
    Remove File          ${DBName}
