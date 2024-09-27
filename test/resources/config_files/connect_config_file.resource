*** Settings ***
Resource    ../common.resource


*** Keywords ***
Connect Using Config File
    [Documentation]    `File name` is only name without extension,
    ...    the path is build relative to the resource directory
    [Arguments]    ${File name}=${None}    &{Params}
    ${Path}=    Set Variable    ${CURDIR}/${File name}.cfg
    Connect To Database    dbConfigFile=${Path}    &{Params}
