#  Copyright (c) 2010 Franz Allan Valencia See
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
from typing import Any, Optional, Tuple

from assertionengine import AssertionOperator, verify_assertion
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from robot.utils import timestr_to_secs

from .params_decorator import renamed_args


class Assertion:
    """
    Assertion handles all the assertions of Database Library.
    """

    def check_if_exists_in_database(
        self,
        select_statement: str,
        *,
        no_transaction: bool = False,
        msg: Optional[str] = None,
        alias: Optional[str] = None,
        parameters: Optional[Tuple] = None,
    ):
        """
        *DEPRECATED* Use new `Check Row Count` keyword with assertion engine instead.
        The deprecated keyword will be removed in future versions.

        Check if any row would be returned by given the input ``select_statement``. If there are no results, then this will
        throw an AssertionError.

        Set optional input ``no_transaction`` to _True_ to run command without an explicit transaction
        commit or rollback.

        The default error message can be overridden with the ``msg`` argument.

        Use optional ``alias`` parameter to specify what connection should be used for the query if you have more
        than one connection open.

        Use ``parameters`` for query variable substitution (variable substitution syntax may be different
        depending on the database client).

        Examples:
        | Check If Exists In Database | SELECT id FROM person WHERE first_name = 'Franz Allan' |
        | Check If Exists In Database | SELECT id FROM person WHERE first_name = 'John' | msg=my error message |
        | Check If Exists In Database | SELECT id FROM person WHERE first_name = 'Franz Allan' | alias=my_alias |
        | Check If Exists In Database | SELECT id FROM person WHERE first_name = 'John' | no_transaction=True |
        | @{parameters} | Create List |  John |
        | Check If Exists In Database | SELECT id FROM person WHERE first_name = %s | parameters=${parameters} |
        """
        if not self.query(select_statement, no_transaction, alias=alias, parameters=parameters):
            raise AssertionError(
                msg or f"Expected to have have at least one row, but got 0 rows from: '{select_statement}'"
            )

    def check_if_not_exists_in_database(
        self,
        selectStatement: str,
        sansTran: bool = False,
        msg: Optional[str] = None,
        alias: Optional[str] = None,
        parameters: Optional[Tuple] = None,
    ):
        """
        *DEPRECATED* Use new `Check Row Count` keyword with assertion engine instead.
        The deprecated keyword will be removed in future versions.

        This is the negation of `check_if_exists_in_database`.

        Check if no rows would be returned by given the input ``selectStatement``. If there are any results, then this
        will throw an AssertionError.

        Set optional input ``sansTran`` to _True_ to run command without an explicit transaction commit or rollback.

        The default error message can be overridden with the ``msg`` argument.

        Use optional ``alias`` parameter to specify what connection should be used for the query if you have more
        than one connection open.

        Use ``parameters`` for query variable substitution (variable substitution syntax may be different
        depending on the database client).

        Examples:
        | Check If Not Exists In Database | SELECT id FROM person WHERE first_name = 'John' |
        | Check If Not Exists In Database | SELECT id FROM person WHERE first_name = 'Franz Allan' | msg=my error message |
        | Check If Not Exists In Database | SELECT id FROM person WHERE first_name = 'Franz Allan' | alias=my_alias |
        | Check If Not Exists In Database | SELECT id FROM person WHERE first_name = 'John' | sansTran=True |
        | @{parameters} | Create List |  John |
        | Check If Not Exists In Database | SELECT id FROM person WHERE first_name = %s | parameters=${parameters} |
        """
        query_results = self.query(selectStatement, sansTran, alias=alias, parameters=parameters)
        if query_results:
            raise AssertionError(
                msg or f"Expected to have have no rows from '{selectStatement}', but got some rows: {query_results}"
            )

    def row_count_is_0(
        self,
        selectStatement: str,
        sansTran: bool = False,
        msg: Optional[str] = None,
        alias: Optional[str] = None,
        parameters: Optional[Tuple] = None,
    ):
        """
        *DEPRECATED* Use new `Check Row Count` keyword with assertion engine instead.
        The deprecated keyword will be removed in future versions.

        Check if any rows are returned from the submitted ``selectStatement``. If there are, then this will throw an
        AssertionError.

        Set optional input ``sansTran`` to _True_ to run command without an explicit transaction commit or
        rollback.

        The default error message can be overridden with the ``msg`` argument.

        Use optional ``alias`` parameter to specify what connection should be used for the query if you have more
        than one connection open.

        Use ``parameters`` for query variable substitution (variable substitution syntax may be different
        depending on the database client).

        Examples:
        | Row Count is 0 | SELECT id FROM person WHERE first_name = 'Franz Allan' |
        | Row Count is 0 | SELECT id FROM person WHERE first_name = 'Franz Allan' | msg=my error message |
        | Row Count is 0 | SELECT id FROM person WHERE first_name = 'John' | alias=my_alias |
        | Row Count is 0 | SELECT id FROM person WHERE first_name = 'John' | sansTran=True |
        | @{parameters} | Create List |  John |
        | Row Count is 0 | SELECT id FROM person WHERE first_name = %s | parameters=${parameters} |
        """
        num_rows = self.row_count(selectStatement, sansTran, alias=alias, parameters=parameters)
        if num_rows > 0:
            raise AssertionError(msg or f"Expected 0 rows, but {num_rows} were returned from: '{selectStatement}'")

    def row_count_is_equal_to_x(
        self,
        selectStatement: str,
        numRows: str,
        sansTran: bool = False,
        msg: Optional[str] = None,
        alias: Optional[str] = None,
        parameters: Optional[Tuple] = None,
    ):
        """
        *DEPRECATED* Use new `Check Row Count` keyword with assertion engine instead.
        The deprecated keyword will be removed in future versions.

        Check if the number of rows returned from ``selectStatement`` is equal to the value submitted. If not, then this
        will throw an AssertionError.

        Set optional input ``sansTran`` to _True_ to run command without an explicit transaction commit or rollback.

        The default error message can be overridden with the ``msg`` argument.

        Use optional ``alias`` parameter to specify what connection should be used for the query if you have more
        than one connection open.

        Use ``parameters`` for query variable substitution (variable substitution syntax may be different
        depending on the database client).

        Examples:
        | Row Count Is Equal To X | SELECT id FROM person | 1 |
        | Row Count Is Equal To X | SELECT id FROM person | 3 | msg=my error message |
        | Row Count Is Equal To X | SELECT id FROM person WHERE first_name = 'John' | 0 | alias=my_alias |
        | Row Count Is Equal To X | SELECT id FROM person WHERE first_name = 'John' | 0 | sansTran=True |
        | @{parameters} | Create List |  John |
        | Row Count Is Equal To X | SELECT id FROM person WHERE first_name = %s | 0 | parameters=${parameters} |
        """
        num_rows = self.row_count(selectStatement, sansTran, alias=alias, parameters=parameters)
        if num_rows != int(numRows.encode("ascii")):
            raise AssertionError(
                msg or f"Expected {numRows} rows, but {num_rows} were returned from: '{selectStatement}'"
            )

    def row_count_is_greater_than_x(
        self,
        selectStatement: str,
        numRows: str,
        sansTran: bool = False,
        msg: Optional[str] = None,
        alias: Optional[str] = None,
        parameters: Optional[Tuple] = None,
    ):
        """
        *DEPRECATED* Use new `Check Row Count` keyword with assertion engine instead.
        The deprecated keyword will be removed in future versions.

        Check if the number of rows returned from ``selectStatement`` is greater than the value submitted. If not, then
        this will throw an AssertionError.

        Set optional input ``sansTran`` to _True_ to run command without an explicit transaction commit or rollback.

        The default error message can be overridden with the ``msg`` argument.

        Use optional ``alias`` parameter to specify what connection should be used for the query if you have more
        than one connection open.

        Use ``parameters`` for query variable substitution (variable substitution syntax may be different
        depending on the database client).

        Examples:
        | Row Count Is Greater Than X | SELECT id FROM person WHERE first_name = 'John' | 0 |
        | Row Count Is Greater Than X | SELECT id FROM person WHERE first_name = 'John' | 0 | msg=my error message |
        | Row Count Is Greater Than X | SELECT id FROM person WHERE first_name = 'John' | 0 | alias=my_alias |
        | Row Count Is Greater Than X | SELECT id FROM person | 1 | sansTran=True |
        | @{parameters} | Create List |  John |
        | Row Count Is Greater Than X | SELECT id FROM person WHERE first_name = %s | 0 | parameters=${parameters} |
        """
        num_rows = self.row_count(selectStatement, sansTran, alias=alias, parameters=parameters)
        if num_rows <= int(numRows.encode("ascii")):
            raise AssertionError(
                msg or f"Expected more than {numRows} rows, but {num_rows} were returned from '{selectStatement}'"
            )

    def row_count_is_less_than_x(
        self,
        selectStatement: str,
        numRows: str,
        sansTran: bool = False,
        msg: Optional[str] = None,
        alias: Optional[str] = None,
        parameters: Optional[Tuple] = None,
    ):
        """
        *DEPRECATED* Use new `Check Row Count` keyword with assertion engine instead.
        The deprecated keyword will be removed in future versions.

        Check if the number of rows returned from ``selectStatement`` is less than the value submitted. If not, then this
        will throw an AssertionError.

        Set optional input ``sansTran`` to _True_ to run command without an explicit transaction commit or rollback.

        Using optional ``msg`` to override the default error message:

        Use optional ``alias`` parameter to specify what connection should be used for the query if you have more
        than one connection open.

        Use ``parameters`` for query variable substitution (variable substitution syntax may be different
        depending on the database client).

        Examples:
        | Row Count Is Less Than X | SELECT id FROM person WHERE first_name = 'John' | 1 |
        | Row Count Is Less Than X | SELECT id FROM person WHERE first_name = 'John' | 2 | msg=my error message |
        | Row Count Is Less Than X | SELECT id FROM person WHERE first_name = 'John' | 3 | alias=my_alias |
        | Row Count Is Less Than X | SELECT id FROM person WHERE first_name = 'John' | 4 | sansTran=True |
        | @{parameters} | Create List |  John |
        | Row Count Is Less Than X | SELECT id FROM person WHERE first_name = %s | 5 | parameters=${parameters} |
        """
        num_rows = self.row_count(selectStatement, sansTran, alias=alias, parameters=parameters)
        if num_rows >= int(numRows.encode("ascii")):
            raise AssertionError(
                msg or f"Expected less than {numRows} rows, but {num_rows} were returned from '{selectStatement}'"
            )

    @renamed_args(mapping={"selectStatement": "select_statement", "sansTran": "no_transaction"})
    def check_row_count(
        self,
        select_statement: str,
        assertion_operator: AssertionOperator,
        expected_value: int,
        assertion_message: Optional[str] = None,
        no_transaction: bool = False,
        alias: Optional[str] = None,
        parameters: Optional[Tuple] = None,
        retry_timeout="0 seconds",
        retry_pause="0.5 seconds",
        *,
        replace_robot_variables=False,
        selectStatement: Optional[str] = None,
        sansTran: Optional[bool] = None,
    ):
        """
        Check the number of rows returned from ``select_statement`` using ``assertion_operator``
        and ``expected_value``. See `Inline assertions` for more details.

        Use ``assertion_message`` to override the default error message.

        Set ``no_transaction`` to _True_ to run command without explicit transaction rollback in case of error.
        See `Commit behavior` for details.

        Use ``alias`` to specify what connection should be used if `Handling multiple database connections`.

        Use ``parameters`` for query variable substitution (variable substitution syntax may be different
        depending on the database client).

        Use ``retry_timeout`` and ``retry_pause`` parameters to enable waiting for assertion to pass.
        See `Retry mechanism` for more details.

        Set ``replace_robot_variables`` to resolve RF variables like _${MY_VAR}_ before executing the SQL.

        === Some parameters were renamed in version 2.0 ===
        The old parameters ``selectStatement`` and ``sansTran`` are *deprecated*,
        please use new parameters ``select_statement`` and ``no_transaction`` instead.

        *The old parameters will be removed in future versions.*

        === Examples ===
        | Check Row Count | SELECT id FROM person WHERE first_name = 'John' | *==* | 1 |
        | Check Row Count | SELECT id FROM person WHERE first_name = 'John' | *>=* | 2 | assertion_message=my error message |
        | Check Row Count | SELECT id FROM person WHERE first_name = 'John' | *inequal* | 3 | alias=my_alias |
        | Check Row Count | SELECT id FROM person WHERE first_name = 'John' | *less than* | 4 | no_transaction=True |
        | @{parameters} | Create List |  John |
        | Check Row Count | SELECT id FROM person WHERE first_name = %s | *equals* | 5 | parameters=${parameters} |
        """
        check_ok = False
        time_counter = 0
        while not check_ok:
            try:
                num_rows = self.row_count(
                    select_statement,
                    no_transaction=no_transaction,
                    alias=alias,
                    parameters=parameters,
                    replace_robot_variables=replace_robot_variables,
                )
                verify_assertion(num_rows, assertion_operator, expected_value, "Wrong row count:", assertion_message)
                check_ok = True
            except AssertionError as e:
                if time_counter >= timestr_to_secs(retry_timeout):
                    logger.info(f"Timeout '{retry_timeout}' reached")
                    raise e
                BuiltIn().sleep(retry_pause)
                time_counter += timestr_to_secs(retry_pause)

    @renamed_args(mapping={"selectStatement": "select_statement", "sansTran": "no_transaction"})
    def check_query_result(
        self,
        select_statement: str,
        assertion_operator: AssertionOperator,
        expected_value: Any,
        row=0,
        col=0,
        assertion_message: Optional[str] = None,
        no_transaction: bool = False,
        alias: Optional[str] = None,
        parameters: Optional[Tuple] = None,
        retry_timeout="0 seconds",
        retry_pause="0.5 seconds",
        *,
        replace_robot_variables=False,
        selectStatement: Optional[str] = None,
        sansTran: Optional[bool] = None,
    ):
        """
        Check value in query result returned from ``select_statement`` using ``assertion_operator`` and ``expected_value``.
        The value position in results can be adjusted using ``row`` and ``col`` parameters (0-based).
        See `Inline assertions` for more details.

        *The assertion in this keyword is type sensitive!*
        The ``expected_value`` is taken as a string, no argument conversion is performed.
        Use RF syntax like ``${1}`` for numeric values.

        Use optional ``assertion_message`` to override the default error message.

        Set ``no_transaction`` to _True_ to run command without explicit transaction rollback in case of error.
        See `Commit behavior` for details.

        Use ``alias`` to specify what connection should be used if `Handling multiple database connections`.

        Use ``parameters`` for query variable substitution (variable substitution syntax may be different
        depending on the database client).

        Use ``retry_timeout`` and ``retry_pause`` parameters to enable waiting for assertion to pass.
        See `Retry mechanism` for more details.

        Set ``replace_robot_variables`` to resolve RF variables like _${MY_VAR}_ before executing the SQL.

        === Some parameters were renamed in version 2.0 ===
        The old parameters ``selectStatement`` and ``sansTran`` are *deprecated*,
        please use new parameters ``select_statement`` and ``no_transaction`` instead.

        *The old parameters will be removed in future versions.*

        === Examples ===
        | Check Query Result | SELECT first_name FROM person | *contains* | Allan |
        | Check Query Result | SELECT first_name, last_name FROM person | *==* | Schneider | row=1 | col=1 |
        | Check Query Result | SELECT id FROM person WHERE first_name = 'John' | *==* | 2 | # Fails, if query returns an integer value |
        | Check Query Result | SELECT id FROM person WHERE first_name = 'John' | *==* | ${2} | # Works, if query returns an integer value |
        | Check Query Result | SELECT first_name FROM person | *equal* | Franz Allan | assertion_message=my error message |
        | Check Query Result | SELECT first_name FROM person | *inequal* | John | alias=my_alias |
        | Check Query Result | SELECT first_name FROM person | *contains* | Allan | no_transaction=True |
        | @{parameters} | Create List |  John |
        | Check Query Result | SELECT first_name FROM person | *contains* | Allan | parameters=${parameters} |
        """
        check_ok = False
        time_counter = 0
        while not check_ok:
            try:
                query_results = self.query(
                    select_statement,
                    no_transaction=no_transaction,
                    alias=alias,
                    parameters=parameters,
                    replace_robot_variables=replace_robot_variables,
                )
                row_count = len(query_results)
                assert (
                    row < row_count
                ), f"Checking row '{row}' is not possible, as query results contain {row_count} rows only!"
                col_count = len(query_results[row])
                assert (
                    col < col_count
                ), f"Checking column '{col}' is not possible, as query results contain {col_count} columns only!"
                actual_value = query_results[row][col]
                verify_assertion(
                    actual_value, assertion_operator, expected_value, "Wrong query result:", assertion_message
                )
                check_ok = True
            except AssertionError as e:
                if time_counter >= timestr_to_secs(retry_timeout):
                    logger.info(f"Timeout '{retry_timeout}' reached")
                    raise e
                BuiltIn().sleep(retry_pause)
                time_counter += timestr_to_secs(retry_pause)

    @renamed_args(mapping={"tableName": "table_name", "sansTran": "no_transaction"})
    def table_must_exist(
        self,
        table_name: str,
        no_transaction: bool = False,
        msg: Optional[str] = None,
        alias: Optional[str] = None,
        *,
        tableName: Optional[str] = None,
        sansTran: Optional[bool] = None,
    ):
        """
        Check if the table with `table_name` exists in the database.

        Use ``msg`` for custom error message.

        Set ``no_transaction`` to _True_ to run command without explicit transaction rollback in case of error.
        See `Commit behavior` for details.

        Use ``alias`` to specify what connection should be used if `Handling multiple database connections`.

        === Some parameters were renamed in version 2.0 ===
        The old parameters ``tableName`` and ``sansTran`` are *deprecated*,
        please use new parameters ``table_name`` and ``no_transaction`` instead.

        *The old parameters will be removed in future versions.*

        === Examples ===
        | Table Must Exist | person |
        | Table Must Exist | person | msg=my error message |
        | Table Must Exist | person | alias=my_alias |
        | Table Must Exist | person | no_transaction=True |
        """
        db_connection = self.connection_store.get_connection(alias)
        if db_connection.module_name in ["cx_Oracle", "oracledb"]:
            query = (
                "SELECT * FROM all_objects WHERE object_type IN ('TABLE','VIEW') AND "
                f"owner = SYS_CONTEXT('USERENV', 'SESSION_USER') AND object_name = UPPER('{table_name}')"
            )
            table_exists = self.row_count(query, no_transaction=no_transaction, alias=alias) > 0
        elif db_connection.module_name in ["sqlite3"]:
            query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}' COLLATE NOCASE"
            table_exists = self.row_count(query, no_transaction=no_transaction, alias=alias) > 0
        elif db_connection.module_name in ["ibm_db", "ibm_db_dbi"]:
            query = f"SELECT name FROM SYSIBM.SYSTABLES WHERE type='T' AND name=UPPER('{table_name}')"
            table_exists = self.row_count(query, no_transaction=no_transaction, alias=alias) > 0
        elif db_connection.module_name in ["teradata"]:
            query = f"SELECT TableName FROM DBC.TablesV WHERE TableKind='T' AND TableName='{table_name}'"
            table_exists = self.row_count(query, no_transaction=no_transaction, alias=alias) > 0
        else:
            try:
                query = f"SELECT * FROM information_schema.tables WHERE table_name='{table_name}'"
                table_exists = self.row_count(query, no_transaction=no_transaction, alias=alias) > 0
            except:
                logger.info("Database doesn't support information schema, try using a simple SQL request")
                try:
                    query = f"SELECT 1 from {table_name} where 1=0"
                    self.row_count(query, no_transaction=no_transaction, alias=alias)
                    table_exists = True
                except:
                    table_exists = False
        assert table_exists, msg or f"Table '{table_name}' does not exist in the db"
