*** Settings ***
Documentation       Keyword 'Disconnect From Database' should work properly if there was no connection at all
...                 or if it was closed previously.
...                 It can be also configured to raise an exception if no connection was open.

Resource            ../../resources/common.resource

Suite Teardown      Disconnect From Database


*** Test Cases ***
Disconnect If No Connection - No Error Expected
    Disconnect From Database

Disconnect If No Connection - Error Expected
    Disconnect From Database
    Run Keyword And Expect Error
    ...    ConnectionError: No open database connection to close
    ...    Disconnect From Database
    ...    error_if_no_connection=True

Disconnect If Connection Was Closed - No Error Expected
    Connect To DB
    Disconnect From Database
    Disconnect From Database

Disconnect If Connection Was Closed - Error Expected
    Connect To DB
    Disconnect From Database
    Run Keyword And Expect Error
    ...    ConnectionError: No open database connection to close
    ...    Disconnect From Database
    ...    error_if_no_connection=True
