*** Settings ***
Documentation       Simulate keyword fails and check that
...                 using custom and starndard error messages work as expected

Resource            ../../resources/common.resource

Suite Setup         Connect To DB
Suite Teardown      Disconnect From Database
Test Setup          Create Person Table And Insert Data
Test Teardown       Drop Tables Person And Foobar


*** Variables ***
${Error Message}            My error message
${Non Existing Select}      SELECT id FROM person WHERE first_name = 'Joe'
${Existing Select}          SELECT id FROM person WHERE first_name = 'Franz Allan'


*** Test Cases ***
Check If Exists In DB Fails
    ${expected error}=    Catenate
    ...    Expected to have have at least one row from
    ...    '${Non Existing Select}'
    ...    but got 0 rows.
    Run Keyword And Expect Error    ${expected error}
    ...    Check If Exists In Database    ${Non Existing Select}

Check If Exists In DB Fails With Message
    Run Keyword And Expect Error    ${Error Message}
    ...    Check If Exists In Database    ${Non Existing Select}
    ...    msg=${Error Message}

Check If Not Exists In DB Fails
    ${expected error}=    Catenate
    ...    Expected to have have no rows from
    ...    '${Existing Select}'
    ...    but got some rows : *
    Run Keyword And Expect Error    ${expected error}
    ...    Check If Not Exists In Database    ${Existing Select}

Check If Not Exists In DB Fails With Message
    Run Keyword And Expect Error    ${Error Message}
    ...    Check If Not Exists In Database    ${Existing Select}
    ...    msg=${Error Message}

Table Must Exist Fails
    ${expected error}=    Catenate
    ...    Table 'nonexistent' does not exist in the db
    Run Keyword And Expect Error    ${expected error}
    ...    Table Must Exist    nonexistent

Table Must Exist Fails With Message
    Run Keyword And Expect Error    ${Error Message}
    ...    Table Must Exist    nonexistent
    ...    msg=${Error Message}

Verify Row Count Is 0 Fails
    ${expected error}=    Catenate
    ...    Expected zero rows to be returned from
    ...    '${Existing Select}'
    ...    but got rows back. Number of rows returned was 1
    Run Keyword And Expect Error    ${expected error}
    ...    Row Count Is 0    ${Existing Select}

Verify Row Count Is 0 Fails With Message
    Run Keyword And Expect Error    ${Error Message}
    ...    Row Count Is 0    ${Existing Select}
    ...    msg=${Error Message}

Verify Row Count Is Equal To X Fails
    ${expected error}=    Catenate
    ...    Expected same number of rows to be returned from
    ...    '${Existing Select}'
    ...    than the returned rows of 1
    Run Keyword And Expect Error    ${expected error}
    ...    Row Count Is Equal To X    ${Existing Select}    9

Verify Row Count Is Equal To X Fails With Message
    Run Keyword And Expect Error    ${Error Message}
    ...    Row Count Is Equal To X
    ...    ${Existing Select}    9    msg=${Error Message}

Verify Row Count Is Less Than X Fails
    ${expected error}=    Catenate
    ...    Expected less rows to be returned from
    ...    '${Existing Select}'
    ...    than the returned rows of 1
    Run Keyword And Expect Error    ${expected error}
    ...    Row Count Is Less Than X
    ...    ${Existing Select}    1

Verify Row Count Is Less Than X Fails With Message
    Run Keyword And Expect Error    ${Error Message}
    ...    Row Count Is Less Than X
    ...    ${Existing Select}    1    msg=${Error Message}

Verify Row Count Is Greater Than X Fails
    ${expected error}=    Catenate
    ...    Expected more rows to be returned from
    ...    '${Existing Select}'
    ...    than the returned rows of 1
    Run Keyword And Expect Error    ${expected error}
    ...    Row Count Is Greater Than X
    ...    ${Existing Select}    1

Verify Row Count Is Greater Than X Fails With Message
    Run Keyword And Expect Error    ${Error Message}
    ...    Row Count Is Greater Than X
    ...    ${Existing Select}    1
    ...    msg=${Error Message}
