*** Settings ***
Documentation       Keyword 'Connect To Database Using Custom Params' should work properly
...                 for different DB modules.

Resource            ../../resources/common.resource

Test Teardown       Disconnect From Database


*** Variables ***
${CONNECTION_STRING}    ${EMPTY}    # the variable is set dynamically depending on the currend DB module


*** Test Cases ***
# ToDo: custom tests for params and string for oracle and psycopg2 and sqlite (this one supports params only)
Connect Using Custom Connection String
    [Documentation]    Connection string provided without additional quotes should work properly.
    ${Connection String}=    Build Connection String
    Connect To Database Using Custom Connection String    ${DB_MODULE}    ${Connection String}

Connect Using Custom Params
    Fail    implement me!