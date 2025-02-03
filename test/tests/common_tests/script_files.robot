*** Settings ***
Resource            ../../resources/common.resource

Suite Setup         Connect To DB
Suite Teardown      Disconnect From Database
Test Setup          Create Person Table
Test Teardown       Drop Tables Person And Foobar


*** Test Cases ***
Semicolons As Statement Separators In One Line
    Run SQL Script File    statements_in_one_line
    ${sql}=    Catenate    select * from person
    ...    where id=6 or id=7
    ${results}=    Query    ${sql}
    Length Should Be    ${results}    2
    Should Be Equal As Strings    ${results}[0]    (6, 'Julian', 'Bashir')
    Should Be Equal As Strings    ${results}[1]    (7, 'Jadzia', 'Dax')

Semicolons In Values
    Run SQL Script File    semicolons_in_values
    ${sql}=    Catenate    select * from person
    ...    where id=3 or id=4
    ${results}=    Query    ${sql}
    Length Should Be    ${results}    2
    Should Be Equal As Strings    ${results}[0]    (3, 'Hello; world', 'Another; value')
    Should Be Equal As Strings    ${results}[1]    (4, 'May the Force; ', 'be with you;')

Semicolons And Quotes In Values
    Run SQL Script File    semicolons_and_quotes_in_values
    ${sql}=    Catenate    select * from person
    ...    where id=5
    ${results}=    Query    ${sql}
    Length Should Be    ${results}    1
    Should Be Equal As Strings    ${results}[0]    (5, 'Miles', "O'Brian")


*** Keywords ***
Run SQL Script File
    [Arguments]    ${File Name}
    ${Script files dir}=    Set Variable    ${CURDIR}/../../resources/script_file_tests
    Execute Sql Script    ${Script files dir}/${File Name}.sql
