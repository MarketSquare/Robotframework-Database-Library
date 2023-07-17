*** Settings ***
Documentation       Tests which work with the same input params across all databases.

Resource            ../../resources/common.resource

Suite Setup         Connect To DB
Suite Teardown      Disconnect From Database
Test Setup          Create Person Table And Insert Data
Test Teardown       Drop Tables Person And Foobar


*** Test Cases ***
SQL Statement Ending With Semicolon Works
    Query    SELECT * FROM person

SQL Statement Ending Without Semicolon Works
    Query    SELECT * FROM person;

Create Person Table
    [Setup]    Log    No setup for this test
    ${output}=    Create Person Table
    Should Be Equal As Strings    ${output}    None

Execute SQL Script - Insert Data In Person table
    [Setup]    Create Person Table
    ${output}=    Insert Data In Person Table Using SQL Script
    Should Be Equal As Strings    ${output}    None

Execute SQL String - Create Foobar Table
    [Setup]    Log    No setup for this test
    ${output}=    Create Foobar Table
    Should Be Equal As Strings    ${output}    None

Simple Select With Multiple Rows
    ${output}=    Query    select LAST_NAME from person
    Length Should Be    ${output}    2
    Should Be Equal    ${output}[0][0]    See
    Should Be Equal    ${output}[1][0]    Schneider

Check If Exists In DB - Franz Allan
    Check If Exists In Database    SELECT id FROM person WHERE FIRST_NAME= 'Franz Allan'

Check If Not Exists In DB - Joe
    Check If Not Exists In Database    SELECT id FROM person WHERE FIRST_NAME= 'Joe'

Table Must Exist - person
    Table Must Exist    person

Verify Row Count is 0
    Row Count is 0    SELECT * FROM person WHERE FIRST_NAME= 'NotHere'

Verify Row Count is Equal to X
    Row Count is Equal to X    SELECT id FROM person    2

Verify Row Count is Less Than X
    Row Count is Less Than X    SELECT id FROM person    3

Verify Row Count is Greater Than X
    Row Count is Greater Than X    SELECT * FROM person    1

Retrieve Row Count
    ${output}=    Row Count    SELECT id FROM person
    Log    ${output}
    Should Be Equal As Strings    ${output}    2

Retrieve records from person table
    ${output}=    Execute SQL String    SELECT * FROM person
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify Query - Row Count person table
    ${output}=    Query    SELECT COUNT(*) FROM person
    Log    ${output}
    Should Be Equal As Integers    ${output}[0][0]    2

Verify Query - Row Count foobar table
    [Setup]    Create Foobar Table
    ${output}=    Query    SELECT COUNT(*) FROM foobar
    Log    ${output}
    Should Be Equal As Integers    ${output}[0][0]    0

Verify Query - Get results as a list of dictionaries
    ${output}=    Query    SELECT * FROM person    returnAsDict=True
    Log    ${output}
    # some databases lower field names and you can't do anything about it
    TRY
        ${value 1}=    Get From Dictionary    ${output}[0]    FIRST_NAME
    EXCEPT    Dictionary does not contain key 'FIRST_NAME'.
        ${value 1}=    Get From Dictionary    ${output}[0]    first_name
    END
    TRY
        ${value 2}=    Get From Dictionary    ${output}[1]    FIRST_NAME
    EXCEPT    Dictionary does not contain key 'FIRST_NAME'.
        ${value 2}=    Get From Dictionary    ${output}[1]    first_name
    END
    Should Be Equal As Strings    ${value 1}    Franz Allan
    Should Be Equal As Strings    ${value 2}    Jerry

Verify Execute SQL String - Row Count person table
    ${output}=    Execute SQL String    SELECT COUNT(*) FROM person
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify Execute SQL String - Row Count foobar table
    [Setup]    Create Foobar Table
    ${output}=    Execute SQL String    SELECT COUNT(*) FROM foobar
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Insert Data Into Table foobar
    [Setup]    Create Foobar Table
    ${output}=    Execute SQL String    INSERT INTO foobar VALUES(1,'Jerry')
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Verify Query - Row Count foobar table 1 row
    [Setup]    Create Foobar Table And Insert Data
    ${output}=    Query    SELECT COUNT(*) FROM foobar
    Log    ${output}
    Should Be Equal As Integers    ${output}[0][0]    1

Verify Delete All Rows From Table - foobar
    [Setup]    Create Foobar Table And Insert Data
    Delete All Rows From Table    foobar

Verify Query - Row Count foobar table 0 row
    [Setup]    Create Foobar Table And Insert Data
    Delete All Rows From Table    foobar
    Row Count Is 0    SELECT * FROM foobar
