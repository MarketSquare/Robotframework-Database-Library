*** Settings ***
Suite Setup       Connect To Database    psycopg2    ${DBName}    ${DBUser}    ${DBPass}    ${DBHost}    ${DBPort}
Suite Teardown    Disconnect From Database
Library           DatabaseLibrary
Library           OperatingSystem

*** Test Cases ***
Check If Exists In Database
    Comment
    Check If Exists In Database    SELECT name FROM data_formats WHERE name = 'ASN-0';

Check If Not Exists In Database
    Comment
    Check If Not Exists In Database    SELECT name FROM data_formats WHERE name = 'ASN-0-Not';

Verify Row Count
    Comment
    ${output} =    Row Count    SELECT name FROM data_formats WHERE name = 'ASN-0';
    Log    ${output}
    Should Be Equal As Integers    ${output}    ${1}

Verify Row Count is 0
    Row Count is 0    SELECT name FROM data_formats WHERE name = 'foobar';

Verify Row Count is Equal to X
    Row Count is Equal to X    SELECT name FROM data_formats WHERE name = 'ASN-0';    1

Verify Row Count is Less Than X
    Row Count is Less Than X    SELECT name FROM data_formats WHERE name = 'ASN-0';    2

Verify Row Count is Greater Than X
    Row Count is Greater Than X    SELECT name FROM data_formats WHERE name = 'ASN-0';    0

Query
    Comment
    @{queryResults} =    Query    SELECT name FROM data_formats;
    Log Many    @{queryResults}

Description
    Comment
    @{queryResults} =    Description    SELECT name FROM data_formats LIMIT 1;
    Log Many    @{queryResults}

Execute Sql Script
    @{results} =    Execute Sql Script    ./testing.sql
    Log Many    @{results}

Table Exist - data_formats
    Table Must Exist    data_formats

Retrieve records from data_formats table
    ${output} =    Execute SQL String    SELECT * FROM data_formats;
    Log    ${output}
    Should Be Equal As Strings    ${output}    None
