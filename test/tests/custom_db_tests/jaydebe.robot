*** Settings ***
Documentation       Test connecting to an Oracle database using jaydebeapi.
...                 Requires Oracle JDBC driver installed and put to the `DRIVER_PATH`.

Resource            ../../resources/common.resource


*** Variables ***
${DRIVER_PATH}          ${CURDIR}/ojdbc17.jar
${DRIVER_CLASSNAME}     oracle.jdbc.driver.OracleDriver
${DB_MODULE}            jaydebeapi
${DB_HOST}              127.0.0.1
${DB_PORT}              1521
${DB_NAME}              db
${JDBC_URL}             jdbc:oracle:thin:@${DB_HOST}:${DB_PORT}/${DB_NAME}
&{DRIVER_ARGS}          user=db_user    password=pass


*** Test Cases ***
Regular Connect
    Connect To Database    ${DB_MODULE}
    ...    jclassname=${DRIVER_CLASSNAME}
    ...    url=${JDBC_URL}
    ...    driver_args=${DRIVER_ARGS}
    ...    jars=${DRIVER_PATH}

Deprecated Connect
    Connect To Database Using Custom Params
    ...    ${DB_MODULE}
    ...    '${DRIVER_CLASSNAME}', '${JDBC_URL}', ['${DB_USER}', '${DB_PASS}'], '${DRIVER_PATH}'
