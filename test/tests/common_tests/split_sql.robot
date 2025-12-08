*** Settings ***
Documentation    Tests for the splitting SQL scripts and string into separate statements.
...
...    First time implementation of the _split_ parameter see in:
...    https://github.com/MarketSquare/Robotframework-Database-Library/issues/184

Resource            ../../resources/common.resource
Suite Setup         Connect To DB
Suite Teardown      Disconnect From Database
Test Setup          Create Person Table
Test Teardown       Drop Tables Person And Foobar

*** Variables ***
@{SQL Commands No Semicolons}
...    SELECT * FROM person
...    SELECT * FROM person WHERE id=1

@{SQL Commands With Semicolons}
...    SELECT * FROM person;
...    SELECT * FROM person WHERE id=1;

*** Test Cases ***
Run Script With Commands Splitting
    [Documentation]    Such a simple script works always,
    ...    just check in the logs if the parameter value was processed properly
    Run SQL Script File    insert_data_in_person_table    split=True

Run Script Without Commands Splitting
    [Documentation]    Running such a script as a single statement works for PostgreSQL,
    ...    but fails in Oracle. Check in the logs if the splitting was disabled.
    Skip If    $DB_MODULE != "psycopg2"
    Run SQL Script File    insert_data_in_person_table    split=False

Run Script Split With External Parser
    [Documentation]    We don't want to test the external parser itself, but just assure
    ...    the parameter works properly
    Run SQL Script File    insert_data_in_person_table    split=True    external_parser=True

Run Script With Semicolons As Statement Separators In One Line
    Run SQL Script File    statements_in_one_line    split=True
    ${sql}=    Catenate    select * from person
    ...    where id=6 or id=7
    ${results}=    Query    ${sql}
    Length Should Be    ${results}    2
    Should Be Equal As Strings    ${results}[0]    (6, 'Julian', 'Bashir')
    Should Be Equal As Strings    ${results}[1]    (7, 'Jadzia', 'Dax')

Run Script With Semicolons In Values
    Run SQL Script File    semicolons_in_values    split=True
    ${sql}=    Catenate    select * from person
    ...    where id=3 or id=4
    ${results}=    Query    ${sql}
    Length Should Be    ${results}    2
    Should Be Equal As Strings    ${results}[0]    (3, 'Hello; world', 'Another; value')
    Should Be Equal As Strings    ${results}[1]    (4, 'May the Force; ', 'be with you;')

Run Script With Semicolons And Quotes In Values
    Run SQL Script File    semicolons_and_quotes_in_values    split=True
    ${sql}=    Catenate    select * from person
    ...    where LAST_NAME='O''Brian'
    ${results}=    Query    ${sql}
    Length Should Be    ${results}    2
    Should Be Equal As Strings    ${results}[0]    (5, 'Miles', "O'Brian")
    Should Be Equal As Strings    ${results}[1]    (6, 'Keiko', "O'Brian")

Split Script Into Statements - Internal Parser
    Insert Data In Person Table Using SQL Script
    ${extracted commands}=    Split Sql Script    ${Script files dir}/split_commands.sql
    Lists Should Be Equal    ${SQL Commands No Semicolons}    ${extracted commands}
    FOR    ${command}    IN    @{extracted commands}
        ${results}=    Query    ${command}
    END

Split Script Into Statements - External Parser
    Insert Data In Person Table Using SQL Script
    ${extracted commands}=    Split Sql Script    ${Script files dir}/split_commands.sql    external_parser=True
    Lists Should Be Equal    ${SQL Commands With Semicolons}    ${extracted commands}
    FOR    ${command}    IN    @{extracted commands}
        ${results}=    Query    ${command}
    END

Split Script Into Statements - External Parser - Comments Are Removed
    Insert Data In Person Table Using SQL Script
    ${extracted commands}=    Split Sql Script    ${Script files dir}/split_commands_comments.sql    external_parser=True
    Lists Should Be Equal    ${SQL Commands With Semicolons}    ${extracted commands}
    FOR    ${command}    IN    @{extracted commands}
        ${results}=    Query    ${command}
    END

Split SQL String Into Statements - Internal Parser
    Insert Data In Person Table Using SQL Script
    ${merged command}=    Catenate    @{SQL Commands With Semicolons}
    ${extracted commands}=    Split Sql String    ${merged command}
    Lists Should Be Equal    ${extracted commands}    ${SQL Commands No Semicolons}
    
Split SQL String Into Statements - External Parser
    Insert Data In Person Table Using SQL Script
    ${merged command}=    Catenate    @{SQL Commands With Semicolons}
    ${extracted commands}=    Split Sql String    ${merged command}    external_parser=True
    Lists Should Be Equal    ${extracted commands}    ${SQL Commands With Semicolons}

Execute SQL String Without Splitting
    [Documentation]    Running such a command as a single statement works for PostgreSQL,
    ...    but fails in Oracle. Check in the logs if the splitting was disabled.
    Skip If    $DB_MODULE != "psycopg2"
    Insert Data In Person Table Using SQL Script
    ${merged command}=    Catenate    @{SQL Commands With Semicolons}
    Execute Sql String    ${merged command}    split=False

Execute SQL String With Splitting - Internal Parser
    Insert Data In Person Table Using SQL Script
    ${merged command}=    Catenate    @{SQL Commands With Semicolons}
    Execute Sql String    ${merged command}    split=True

Execute SQL String With Splitting - External Parser
    Insert Data In Person Table Using SQL Script
    ${merged command}=    Catenate    @{SQL Commands With Semicolons}
    Execute Sql String    ${merged command}    split=True    external_parser=True

*** Keywords ***
Run SQL Script File
    [Arguments]    ${File Name}    ${split}    ${external_parser}=False
    Execute Sql Script    ${Script files dir}/${File Name}.sql    split=${Split}    external_parser=${external_parser}
