*** Settings ***
Resource            ../../resources/common.resource
Suite Setup    Skip If    "${DB_MODULE}" == "sqlite3"
...    Aliases tests don't work for SQLite as each connection is always a new file

Test Setup         Connect, Create Some Data And Disconnect
Test Teardown      Connect, Clean Up Data And Disconnect


*** Test Cases ***
Connections Can Be Aliased
    Connect To DB    # default alias
    Connect To DB    alias=second

Default Alias Can Be Empty
    Connect To DB    # default alias
    Query    SELECT * FROM person
    Connect To DB    alias=second
    Query    SELECT * FROM person
    Query    SELECT * FROM person    alias=second

Switch From Default And Disconnect
    Connect To DB    # default alias
    Connect To DB    alias=second
    Switch Database    second
    Query    SELECT * FROM person    # query with 'second' connection
    Disconnect From Database    alias=second
    Query    SELECT * FROM person    # query with 'default' connection

Disconnect Not Existing Alias
    Connect To DB    # default alias
    Disconnect From Database    alias=idontexist    # silent warning
    Run Keyword And Expect Error    ConnectionError: No open database connection to close
    ...    Disconnect From Database    alias=idontexist    error_if_no_connection=${True}
    # default alias exist and can be closed
    Disconnect From Database    error_if_no_connection=${True}

Switch Not Existing Alias
    Run Keyword And Expect Error    ValueError: Alias 'second' not found in existing connections.
    ...    Switch Database    second

Execute SQL Script - Insert Data In Person table
    [Setup]    Connect, Create Some Data And Disconnect    Run SQL script=${False}
    Connect To DB    alias=aliased_conn
    ${output}    Insert Data In Person Table Using SQL Script    alias=aliased_conn
    Should Be Equal As Strings    ${output}    None

Check If Exists In DB - Franz Allan
    Connect To DB    alias=aliased_conn
    Check If Exists In Database    SELECT id FROM person WHERE FIRST_NAME= 'Franz Allan'    alias=aliased_conn

Check If Not Exists In DB - Joe
    Connect To DB    alias=aliased_conn
    Check If Not Exists In Database    SELECT id FROM person WHERE FIRST_NAME= 'Joe'    alias=aliased_conn

Table Must Exist - person
    Connect To DB    alias=aliased_conn
    Table Must Exist    person    alias=aliased_conn

Verify Row Count is 0
    Connect To DB    alias=aliased_conn
    Row Count is 0    SELECT * FROM person WHERE FIRST_NAME= 'NotHere'    alias=aliased_conn

Verify Row Count is Equal to X
    Connect To DB    alias=aliased_conn
    Row Count is Equal to X    SELECT id FROM person    2    alias=aliased_conn

Verify Row Count is Less Than X
    Connect To DB    alias=aliased_conn
    Row Count is Less Than X    SELECT id FROM person    3    alias=aliased_conn

Verify Row Count is Greater Than X
    Connect To DB    alias=aliased_conn
    Row Count is Greater Than X    SELECT * FROM person    1    alias=aliased_conn

Retrieve Row Count
    Connect To DB    alias=aliased_conn
    ${output}    Row Count    SELECT id FROM person    alias=aliased_conn
    Log    ${output}
    Should Be Equal As Strings    ${output}    2

Retrieve records from person table
    Connect To DB    alias=aliased_conn
    ${output}    Execute SQL String    SELECT * FROM person
    Log    ${output}
    Should Be Equal As Strings    ${output}    None

Use Last Connected If Not Alias Provided
    Connect To DB    alias=aliased_conn
    ${output}    Query    SELECT COUNT(*) FROM person
    Log    ${output}
    Should Be Equal As Integers    ${output}[0][0]    2

Verify Query - Get results as a list of dictionaries
    Connect To DB    alias=aliased_conn
    ${output}    Query    SELECT * FROM person    returnAsDict=True    alias=aliased_conn
    Log    ${output}
    # some databases lower field names and you can't do anything about it
    TRY
        ${value 1}    Get From Dictionary    ${output}[0]    FIRST_NAME
    EXCEPT    Dictionary does not contain key 'FIRST_NAME'.
        ${value 1}    Get From Dictionary    ${output}[0]    first_name
    END
    TRY
        ${value 2}    Get From Dictionary    ${output}[1]    FIRST_NAME
    EXCEPT    Dictionary does not contain key 'FIRST_NAME'.
        ${value 2}    Get From Dictionary    ${output}[1]    first_name
    END
    Should Be Equal As Strings    ${value 1}    Franz Allan
    Should Be Equal As Strings    ${value 2}    Jerry

Verify Delete All Rows From Table
    Connect To DB    alias=aliased_conn
    Delete All Rows From Table    person    alias=aliased_conn
    Row Count Is 0    SELECT * FROM person    alias=aliased_conn


*** Keywords ***
Connect, Create Some Data And Disconnect
    [Arguments]    ${Run SQL script}=${True}
    Connect To DB
    Create Person Table
    IF    $Run_SQL_script
        Insert Data In Person Table Using SQL Script
    END
    Disconnect From Database

Connect, Clean Up Data And Disconnect
    Disconnect From All Databases
    Connect To DB
    Drop Tables Person And Foobar
    Disconnect From Database
