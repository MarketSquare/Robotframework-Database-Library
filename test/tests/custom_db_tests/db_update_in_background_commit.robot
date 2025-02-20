*** Settings ***
Documentation       Check if the SQL statement returns new results, if DB is being updated in the background -
...                 this requires a commit after each query.
...                 See https://github.com/MarketSquare/Robotframework-Database-Library/issues/237

Resource            ../../resources/common.resource

Suite Setup         Connect To DB
Suite Teardown      Disconnect From Database
Test Setup          Create Person Table And Insert Data
Test Teardown       Drop Tables Person And Foobar


*** Test Cases ***
Use Auto retry
    [Documentation]    Update the DB manually in the background and check if the query returns the new results
    Check Query Result    SELECT LAST_NAME FROM person ORDER BY id    ==    Musk    retry_timeout=30s
