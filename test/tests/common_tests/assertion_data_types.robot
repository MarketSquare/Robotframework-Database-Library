*** Settings ***
Documentation       Simulate data type mismatch, check error messages and try converting to strings

Resource            ../../resources/common.resource

Suite Setup         Connect To DB
Suite Teardown      Disconnect From Database
Test Setup          Create Person Table And Insert Data
Test Teardown       Drop Tables Person And Foobar


*** Variables ***
${sql}      SELECT id FROM person WHERE first_name = 'Franz Allan'


*** Test Cases ***
Int Contains String - Type Error
    Run Keyword And Expect Error    TypeError: Invalid assertion*
    ...    Check Query Result    ${sql}    contains    1

Assert As String - Int Contains String
   Check Query Result    ${sql}    contains    1    assert_as_string=True

Int Equals String - Not Equals Error Message
    Run Keyword And Expect Error    Wrong query result*
    ...    Check Query Result    ${sql}    ==    1

Assert As String - Int Equals String
    Check Query Result    ${sql}    ==    1    assert_as_string=True

Int > String - Type Error
    Run Keyword And Expect Error    TypeError: Invalid assertion*
    ...    Check Query Result    ${sql}    >   1

Int > String - Wrong Result Error
    Run Keyword And Expect Error    Wrong query result*
    ...    Check Query Result    ${sql}    >    1    assert_as_string=True

Int Equals Int - Not Equals Error Message
    Run Keyword And Expect Error    Wrong query result*
    ...    Check Query Result    ${sql}    ==    ${2}

Assert As String - Int Equals Int - Not Equals Error Message
    Run Keyword And Expect Error    Wrong query result*
    ...    Check Query Result    ${sql}    ==    ${2}    assert_as_string=True

Int Contains Int - Type Error
    Run Keyword And Expect Error    TypeError: Invalid assertion*
    ...    Check Query Result    ${sql}    contains    ${1}

Assert As String - Int Contains Int
    Check Query Result    ${sql}    contains    ${1}    assert_as_string=True

