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

import importlib
import inspect
import re
import sys
from typing import List, Optional, Tuple

import sqlparse
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from robot.utils.dotdict import DotDict

from .connection_manager import Connection
from .params_decorator import renamed_args


class Query:
    """
    Query handles all the querying done by the Database Library.
    """

    def __init__(self, log_query_results, log_query_results_head):
        self.LOG_QUERY_RESULTS = log_query_results
        self.LOG_QUERY_RESULTS_HEAD = log_query_results_head

    @renamed_args(
        mapping={"selectStatement": "select_statement", "sansTran": "no_transaction", "returnAsDict": "return_dict"}
    )
    def query(
        self,
        select_statement: str,
        no_transaction: bool = False,
        return_dict: bool = False,
        alias: Optional[str] = None,
        parameters: Optional[Tuple] = None,
        *,
        replace_robot_variables=False,
        selectStatement: Optional[str] = None,
        sansTran: Optional[bool] = None,
        returnAsDict: Optional[bool] = None,
    ):
        """
        Runs a query with the ``select_statement`` and returns the result as list of rows.
        The type of row values depends on the database module -
        usually they are tuples or tuple-like objects.

        Set ``no_transaction`` to _True_ to run command without explicit transaction commit or rollback in case of error.
        See `Commit behavior` for details.

        Set ``return_dict`` to _True_ to explicitly convert the return values into list of dictionaries.

        Use ``alias`` to specify what connection should be used if `Handling multiple database connections`.

        Use ``parameters`` for query variable substitution (variable substitution syntax may be different
        depending on the database client).

        Set ``replace_robot_variables`` to resolve RF variables like _${MY_VAR}_ before executing the SQL.

        === Some parameters were renamed in version 2.0 ===
        The old parameters ``selectStatement``, ``sansTran`` and ``returnAsDict`` are *deprecated*,
        please use new parameters ``select_statement``, ``no_transaction`` and ``return_dict`` instead.

        *The old parameters will be removed in future versions.*

        === Examples ===
        | ${Results}=    | Query | select LAST_NAME from person |
        | ${Results}=    | Query | select LAST_NAME from person | no_transaction=True |
        | ${Results}=    | Query | select LAST_NAME from person | return_dict=True |
        | ${Results}=    | Query | select LAST_NAME from person | alias=postgres |
        | @{parameters} | Create List |  person |
        | ${Results}=   | Query | SELECT * FROM %s | parameters=${parameters} |
        """
        db_connection = self.connection_store.get_connection(alias)
        cur = None
        try:
            cur = db_connection.client.cursor()
            self._execute_sql(
                cur,
                select_statement,
                parameters=parameters,
                omit_trailing_semicolon=db_connection.omit_trailing_semicolon,
                replace_robot_variables=replace_robot_variables,
            )
            all_rows = cur.fetchall()
            if all_rows is None:
                all_rows = []
            self._commit_if_needed(db_connection, no_transaction)
            col_names = [c[0] for c in cur.description]
            self._log_query_results(col_names, all_rows)
            if return_dict:
                return [DotDict(zip(col_names, row)) for row in all_rows]
            return all_rows
        except Exception as e:
            self._rollback_and_raise(db_connection, no_transaction, e)

    @renamed_args(mapping={"selectStatement": "select_statement", "sansTran": "no_transaction"})
    def row_count(
        self,
        select_statement: str,
        no_transaction: bool = False,
        alias: Optional[str] = None,
        parameters: Optional[Tuple] = None,
        *,
        replace_robot_variables=False,
        selectStatement: Optional[str] = None,
        sansTran: Optional[bool] = None,
    ):
        """
        Runs a query with the ``select_statement`` and returns the number of rows in the result.

        Set ``no_transaction`` to _True_ to run command without explicit transaction commit or rollback in case of error.
        See `Commit behavior` for details.

        Use ``alias`` to specify what connection should be used if `Handling multiple database connections`.

        Use ``parameters`` for query variable substitution (variable substitution syntax may be different
        depending on the database client).

        Set ``replace_robot_variables`` to resolve RF variables like _${MY_VAR}_ before executing the SQL.

        === Some parameters were renamed in version 2.0 ===
        The old parameters ``selectStatement`` and ``sansTran`` are *deprecated*,
        please use new parameters ``select_statement`` and ``no_transaction`` instead.

        *The old parameters will be removed in future versions.*

        === Examples ===
        | ${Rows}=    | Row Count | select LAST_NAME from person |
        | ${Rows}=    | Row Count | select LAST_NAME from person | no_transaction=True |
        | ${Rows}=    | Row Count | select LAST_NAME from person | alias=postgres |
        | @{parameters} | Create List |  person |
        | ${Rows}=   | Row Count | SELECT * FROM %s | parameters=${parameters} |
        """
        db_connection = self.connection_store.get_connection(alias)
        cur = None
        try:
            cur = db_connection.client.cursor()
            self._execute_sql(
                cur,
                select_statement,
                parameters=parameters,
                omit_trailing_semicolon=db_connection.omit_trailing_semicolon,
                replace_robot_variables=replace_robot_variables,
            )
            data = cur.fetchall()
            if data is None:
                data = []
            self._commit_if_needed(db_connection, no_transaction)
            col_names = [c[0] for c in cur.description]
            if db_connection.module_name in ["sqlite3", "ibm_db", "ibm_db_dbi", "pyodbc", "jaydebeapi"]:
                current_row_count = len(data)
            else:
                current_row_count = cur.rowcount
            logger.info(f"Retrieved {current_row_count} rows")
            self._log_query_results(col_names, data)
            return current_row_count
        except Exception as e:
            self._rollback_and_raise(db_connection, no_transaction, e)

    @renamed_args(mapping={"selectStatement": "select_statement", "sansTran": "no_transaction"})
    def description(
        self,
        select_statement: str,
        no_transaction: bool = False,
        alias: Optional[str] = None,
        parameters: Optional[Tuple] = None,
        *,
        replace_robot_variables=False,
        selectStatement: Optional[str] = None,
        sansTran: Optional[bool] = None,
    ):
        """
        Runs a query with the ``select_statement`` to determine the table description.

        Set ``no_transaction`` to _True_ to run command without explicit transaction commit or rollback in case of error.
        See `Commit behavior` for details.

        Use ``alias`` to specify what connection should be used if `Handling multiple database connections`.

        Use ``parameters`` for query variable substitution (variable substitution syntax may be different
        depending on the database client).

        Set ``replace_robot_variables`` to resolve RF variables like _${MY_VAR}_ before executing the SQL.

        === Some parameters were renamed in version 2.0 ===
        The old parameters ``selectStatement`` and ``sansTran`` are *deprecated*,
        please use new parameters ``select_statement`` and ``no_transaction`` instead.

        *The old parameters will be removed in future versions.*

        === Examples ===
        | ${Person table description}=  | Description | select LAST_NAME from person |
        | ${Person table description}=  | Description | select LAST_NAME from person | no_transaction=True |
        | ${Person table description}=  | Description | select LAST_NAME from person | alias=postgres |
        | @{parameters} | Create List |  person |
        | ${Person table description}=   | Description | SELECT * FROM %s | parameters=${parameters} |
        """
        db_connection = self.connection_store.get_connection(alias)
        cur = None
        try:
            cur = db_connection.client.cursor()
            self._execute_sql(
                cur,
                select_statement,
                parameters=parameters,
                omit_trailing_semicolon=db_connection.omit_trailing_semicolon,
                replace_robot_variables=replace_robot_variables,
            )
            self._commit_if_needed(db_connection, no_transaction)
            description = list(cur.description)
            if sys.version_info[0] < 3:
                for row in range(0, len(description)):
                    description[row] = (description[row][0].encode("utf-8"),) + description[row][1:]
            return description
        except Exception as e:
            self._rollback_and_raise(db_connection, no_transaction, e)

    @renamed_args(mapping={"tableName": "table_name", "sansTran": "no_transaction"})
    def delete_all_rows_from_table(
        self,
        table_name: str,
        no_transaction: bool = False,
        alias: Optional[str] = None,
        *,
        tableName: Optional[str] = None,
        sansTran: Optional[bool] = None,
    ):
        """
        Deletes all rows from table with ``table_name``.

        Set ``no_transaction`` to _True_ to run command without explicit transaction commit
        or rollback in case of error.
        See `Commit behavior` for details.

        Use ``alias`` to specify what connection should be used if `Handling multiple database connections`.

        === Some parameters were renamed in version 2.0 ===
        The old parameters ``tableName`` and ``sansTran`` are *deprecated*,
        please use new parameters ``table_name`` and ``no_transaction`` instead.

        *The old parameters will be removed in future versions.*

        === Examples ===
        | Delete All Rows From Table | person |
        | Delete All Rows From Table | person | no_transaction=True |
        | Delete All Rows From Table | person | alias=my_alias |
        """
        db_connection = self.connection_store.get_connection(alias)
        cur = None
        query = f"DELETE FROM {table_name}"
        try:
            cur = db_connection.client.cursor()
            result = self._execute_sql(cur, query)
            self._commit_if_needed(db_connection, no_transaction)
            if result is not None:
                return result
        except Exception as e:
            self._rollback_and_raise(db_connection, no_transaction, e)

    @renamed_args(mapping={"sqlScriptFileName": "script_path", "sansTran": "no_transaction"})
    def execute_sql_script(
        self,
        script_path: str,
        no_transaction: bool = False,
        alias: Optional[str] = None,
        split: bool = True,
        *,
        external_parser=False,
        replace_robot_variables=False,
        sqlScriptFileName: Optional[str] = None,
        sansTran: Optional[bool] = None,
    ):
        """
        Executes the content of the SQL script file loaded from `script_path` as SQL commands.

        SQL commands are expected to be delimited by a semicolon (';') - they will be split and executed separately.
        Set ``split`` to _False_ to disable this behavior  - in this case the entire script content
        will be passed to the database module for execution as a single command.

        Set ``external_parser`` to _True_ to use the external library [https://pypi.org/project/sqlparse/|sqlparse] for splitting the script.

        Set ``no_transaction`` to _True_ to run command without explicit transaction commit
        or rollback in case of error.
        See `Commit behavior` for details.

        Use ``alias`` to specify what connection should be used if `Handling multiple database connections`.

        Set ``replace_robot_variables`` to resolve RF variables like _${MY_VAR}_ before executing the SQL.

        === Some parameters were renamed in version 2.0 ===
        The old parameters ``sqlScriptFileName`` and ``sansTran`` are *deprecated*,
        please use new parameters ``script_path`` and ``no_transaction`` instead.

        *The old parameters will be removed in future versions.*

        === Examples ===
        | Execute SQL Script | insert_data_in_person_table.sql |
        | Execute SQL Script | insert_data_in_person_table.sql | no_transaction=True |
        | Execute SQL Script | insert_data_in_person_table.sql | alias=postgres |
        | Execute SQL Script | insert_data_in_person_table.sql | split=False |
        """
        db_connection = self.connection_store.get_connection(alias)
        cur = None
        try:
            cur = db_connection.client.cursor()
            if not split:
                with open(script_path, encoding="UTF-8") as sql_file:
                    logger.info("Statements splitting disabled - pass entire script content to the database module")
                    self._execute_sql(
                        cur,
                        sql_file.read(),
                        omit_trailing_semicolon=db_connection.omit_trailing_semicolon,
                        replace_robot_variables=replace_robot_variables,
                    )
            else:
                statements_to_execute = self.split_sql_script(script_path, external_parser=external_parser)
                for statement in statements_to_execute:
                    proc_end_pattern = re.compile("end(?!( if;| loop;| case;| while;| repeat;)).*;()?")
                    line_ends_with_proc_end = re.compile(r"(\s|;)" + proc_end_pattern.pattern + "$")
                    omit_semicolon = not line_ends_with_proc_end.search(statement.lower())
                    self._execute_sql(cur, statement, omit_semicolon, replace_robot_variables=replace_robot_variables)
            self._commit_if_needed(db_connection, no_transaction)
        except Exception as e:
            self._rollback_and_raise(db_connection, no_transaction, e)

    def split_sql_script(
        self,
        script_path: str,
        external_parser=False,
    ):
        """
        Splits the content of the SQL script file loaded from ``script_path`` into individual SQL commands
        and returns them as a list of strings.
        SQL commands are expected to be delimited by a semicolon (';').

        Set ``external_parser`` to _True_ to use the external library [https://pypi.org/project/sqlparse/|sqlparse].
        """
        with open(script_path, encoding="UTF-8") as sql_file:
            logger.info("Splitting script file into statements...")
            statements_to_execute = []
            if external_parser:
                statements_to_execute = sqlparse.split(sql_file.read())
            else:
                current_statement = ""
                inside_statements_group = False
                proc_start_pattern = re.compile("create( or replace)? (procedure|function){1}( )?")
                proc_end_pattern = re.compile("end(?!( if;| loop;| case;| while;| repeat;)).*;()?")
                for line in sql_file:
                    line = line.strip()
                    if line.startswith("#") or line.startswith("--") or line == "/":
                        continue

                    # check if the line matches the creating procedure regexp pattern
                    if proc_start_pattern.match(line.lower()):
                        inside_statements_group = True
                    elif line.lower().startswith("begin"):
                        inside_statements_group = True

                    # semicolons inside the line? use them to separate statements
                    # ... but not if they are inside a begin/end block (aka. statements group)
                    sqlFragments = line.split(";")
                    # no semicolons
                    if len(sqlFragments) == 1:
                        current_statement += line + " "
                        continue
                    quotes = 0
                    # "select * from person;" -> ["select..", ""]
                    for sqlFragment in sqlFragments:
                        if len(sqlFragment.strip()) == 0:
                            continue

                        if inside_statements_group:
                            # if statements inside a begin/end block have semicolns,
                            # they must persist - even with oracle
                            sqlFragment += "; "

                        if proc_end_pattern.match(sqlFragment.lower()):
                            inside_statements_group = False
                        elif proc_start_pattern.match(sqlFragment.lower()):
                            inside_statements_group = True
                        elif sqlFragment.lower().startswith("begin"):
                            inside_statements_group = True

                        # check if the semicolon is a part of the value (quoted string)
                        quotes += sqlFragment.count("'")
                        quotes -= sqlFragment.count("\\'")
                        inside_quoted_string = quotes % 2 != 0
                        if inside_quoted_string:
                            sqlFragment += ";"  # restore the semicolon

                        current_statement += sqlFragment
                        if not inside_statements_group and not inside_quoted_string:
                            statements_to_execute.append(current_statement.strip())
                            current_statement = ""
                            quotes = 0

                current_statement = current_statement.strip()
                if len(current_statement) != 0:
                    statements_to_execute.append(current_statement)

            return statements_to_execute

    @renamed_args(
        mapping={
            "sqlString": "sql_string",
            "sansTran": "no_transaction",
            "omitTrailingSemicolon": "omit_trailing_semicolon",
        }
    )
    def execute_sql_string(
        self,
        sql_string: str,
        no_transaction: bool = False,
        alias: Optional[str] = None,
        parameters: Optional[Tuple] = None,
        omit_trailing_semicolon: Optional[bool] = None,
        *,
        replace_robot_variables=False,
        sqlString: Optional[str] = None,
        sansTran: Optional[bool] = None,
        omitTrailingSemicolon: Optional[bool] = None,
    ):
        """
        Executes the ``sql_string`` as a single SQL command.

        Set ``no_transaction`` to _True_ to run command without explicit transaction commit
        or rollback in case of error.
        See `Commit behavior` for details.

        Use ``alias`` to specify what connection should be used if `Handling multiple database connections`.

        Use ``parameters`` for query variable substitution (variable substitution syntax may be different
        depending on the database client).

        Set ``omit_trailing_semicolon`` to explicitly control the `Omitting trailing semicolon behavior` for the command.

        Set ``replace_robot_variables`` to resolve RF variables like _${MY_VAR}_ before executing the SQL.

        === Some parameters were renamed in version 2.0 ===
        The old parameters ``sqlString``, ``sansTran`` and ``omitTrailingSemicolon`` are *deprecated*,
        please use new parameters ``sql_string``, ``no_transaction`` and ``omit_trailing_semicolon`` instead.

        *The old parameters will be removed in future versions.*

        === Examples ===
        | Execute Sql String | DELETE FROM person_employee_table; DELETE FROM person_table |
        | Execute Sql String | DELETE FROM person_employee_table; DELETE FROM person_table | no_transaction=True |
        | Execute Sql String | DELETE FROM person_employee_table; DELETE FROM person_table | alias=my_alias |
        | Execute Sql String | CREATE PROCEDURE proc AS BEGIN DBMS_OUTPUT.PUT_LINE('Hello!'); END; | omit_trailing_semicolon=False |
        | @{parameters} | Create List |  person_employee_table |
        | Execute Sql String | DELETE FROM %s | parameters=${parameters} |
        """
        db_connection = self.connection_store.get_connection(alias)
        cur = None
        try:
            cur = db_connection.client.cursor()
            if omit_trailing_semicolon is None:
                omit_trailing_semicolon = db_connection.omit_trailing_semicolon
            self._execute_sql(
                cur,
                sql_string,
                omit_trailing_semicolon=omit_trailing_semicolon,
                parameters=parameters,
                replace_robot_variables=replace_robot_variables,
            )
            self._commit_if_needed(db_connection, no_transaction)
        except Exception as e:
            self._rollback_and_raise(db_connection, no_transaction, e)

    @renamed_args(mapping={"spName": "procedure_name", "spParams": "procedure_params", "sansTran": "no_transaction"})
    def call_stored_procedure(
        self,
        procedure_name: str,
        procedure_params: Optional[List] = None,
        no_transaction: bool = False,
        alias: Optional[str] = None,
        additional_output_params: Optional[List] = None,
        *,
        spName: Optional[str] = None,
        spParams: Optional[List] = None,
        sansTran: Optional[bool] = None,
    ):
        """
        Calls a stored procedure `procedure_name` with the `procedure_params` - a *list* of parameters the procedure requires.
        *Returns two lists* - the _parameter values_ and the _result sets_.

        Use the special *CURSOR* value for OUT params, which should receive result sets - relevant only for some databases (e.g. Oracle or PostgreSQL).

        Set ``no_transaction`` to _True_ to run command without explicit transaction commit
        or rollback in case of error.
        See `Commit behavior` for details.

        Use ``alias`` to specify what connection should be used if `Handling multiple database connections`.

        Use the ``additional_output_params`` list for OUT params of a procedure in MSSQL.

        === Some parameters were renamed in version 2.0 ===
        The old parameters ``spName``, ``spParams`` and ``sansTran`` are *deprecated*, please use
        new parameters ``procedure_name``, ``procedure_params`` and ``no_transaction`` instead.

        *The old parameters will be removed in future versions.*

        = Handling parameters and result sets =
        Handling the input and output parameters and the result sets is very different
        depending on the database itself and on the Python database driver - i.e. how it implements the `cursor.callproc()` function.

        == Common case (e.g. MySQL) ==
        Generally a procedure call requires all parameter values (IN and OUT) put together in a list - `procedure_params`.

        Calling the procedure returns *two lists*:
        - *Param values* - the copy of procedure parameters (modified, if the procedure changes the OUT params). The list is empty, if procedures receives no params.
        - *Result sets* - the list of lists, each of them containing results of some query, if the procedure returns them.

        == Oracle (oracledb, cx_Oracle) ==
        Oracle procedures work fine with simple IN and OUT params, but require some special handling of result sets.

        === Simple case with IN and OUT params (no result sets) ===
        Consider the following procedure:
        | CREATE OR REPLACE PROCEDURE
        | get_second_name (person_first_name IN VARCHAR, person_second_name OUT VARCHAR) AS
        | BEGIN
        |   SELECT last_name
        |   INTO person_second_name
        |   FROM person
        |   WHERE first_name = person_first_name;
        | END;

        Calling the procedure in Robot Framework:
        | @{params}=         Create List    Jerry    OUTPUT
        | # Second parameter value can be anything, it will be replaced anyway
        |
        | ${param values}    ${result sets}=    Call Stored Procedure    get_second_name    ${params}
        | # ${param values} = ['Jerry', 'Schneider']
        | # ${result sets} = []

        === Oracle procedure returning a result set ===
        If a procedure in Oracle should return a result set, it must take OUT parameters of a special type -
        _SYS_REFCURSOR_.

        Consider the following procedure:
        | get_all_second_names (second_names_cursor OUT SYS_REFCURSOR) AS
        | BEGIN
        |   OPEN second_names_cursor for
        |   SELECT LAST_NAME FROM person;
        | END;

        Calling the procedure in Robot Framework requires the special value *CURSOR* for the OUT parameters,
        they will be converted to appropriate DB variables before calling the procedure.
        | @{params}=    Create List    CURSOR
        | # The parameter must have this special value CURSOR
        |
        | ${param values}    ${result sets}=    Call Stored Procedure    get_all_second_names    ${params}
        | # ${param values} = [<oracledb.Cursor on <oracledb.Connection ...>>]
        | # ${result sets} = [[('Franz Allan',), ('Jerry',)], [('See',), ('Schneider',)]]

        === Oracle procedure returning multiple result sets ===
        If a procedure takes multiple OUT parameters of the _SYS_REFCURSOR_ type, they all must have
        the special *CURSOR* value when calling the procedure:
        | @{params} =        Create List         CURSOR    CURSOR
        | ${param values}    ${result sets} =    Call Stored Procedure    Get_all_first_and_second_names    ${params}
        | # ${param values} = [<oracledb.Cursor on <oracledb.Connection ...>>, <oracledb.Cursor on <oracledb.Connection ...>>]
        | # ${result sets}  = [[('Franz Allan',), ('Jerry',)], [('See',), ('Schneider',)]]

        == PostgreSQL (psycopg2, psycopg3) ==
        PostgreSQL doesn't return single values as params, only as result sets.
        It also supports special handling of result sets over OUT params of a special type (like Oracle).

        === Simple case with IN and OUT params (no CURSOR parameters) ===
        Consider the following procedure:
        | CREATE FUNCTION
        | get_second_name (IN person_first_name VARCHAR(20),
        | OUT person_second_name VARCHAR(20))
        | LANGUAGE plpgsql
        | AS
        | '
        | BEGIN
        |   SELECT LAST_NAME INTO person_second_name
        |   FROM person
        |   WHERE FIRST_NAME = person_first_name;
        | END
        | ';

        Calling the procedure in Robot Framework:
        | @{params}=    Create List    Jerry
        | ${param values}    ${result sets}=    Call Stored Procedure    get_second_name    ${params}
        | # ${param values} = ['Jerry']
        | # ${result sets} = [[('Schneider',)]]

        === PostgreSQL procedure with CURSOR parameters ===
        If a procedure in PostgreSQL should return a proper result set, it must take OUT parameters of a special type -
        _refcursor_.

        Consider the following procedure:
        | CREATE FUNCTION
        | get_all_first_and_second_names(result1 refcursor, result2 refcursor)
        | RETURNS SETOF refcursor
        | LANGUAGE plpgsql
        | AS
        | '
        | BEGIN
        |   OPEN result1 FOR SELECT FIRST_NAME FROM person;
        |   RETURN NEXT result1;
        |   OPEN result2 FOR SELECT LAST_NAME FROM person;
        |   RETURN NEXT result2;
        | END
        | ';

        Calling the procedure in Robot Framework requires the special value *CURSOR* for the OUT parameters,
        they will be converted to appropriate DB variables before calling the procedure.
        | @{params}=    Create List    CURSOR    CURSOR
        | # The parameters must have this special value CURSOR
        |
        | ${param values}    ${result sets}=    Call Stored Procedure    get_all_first_and_second_names    ${params}
        | # ${param values} = ['CURSOR_0', 'CURSOR_1']
        | # ${result sets} = [[('Franz Allan',), ('Jerry',)], [('See',), ('Schneider',)]

        == MS SQL Server (pymssql) ==
        The _pymssql_ driver doesn't natively support getting the OUT parameter values after calling a procedure.
        - This requires special handling of OUT parameters using the `additional_output_params` argument.
        - Furthermore, it's not possible to fetch the OUT parameter values for a procedure, which returns a result set AND has OUT parameters.

        === Simple case with IN and OUT params (no result sets) ===
        Consider the following procedure:
        | CREATE PROCEDURE
        | return_out_param_without_result_sets
        | @my_input VARCHAR(20),
        | @my_output INT OUTPUT
        | AS
        | BEGIN
        |  IF @my_input = 'give me 1'
        |     BEGIN
        |         SELECT @my_output = 1;
        |     END
        |     ELSE
        |     BEGIN
        |         SELECT @my_output = 0;
        |     END
        | END;

        Calling the procedure in Robot Framework requires putting the IN parameters as usual in the `procedure_params` argument,
        but the sample values of OUT parameters must be put in the argument `additional_output_params`.

        | @{params}=    Create List    give me 1
        | @{out_params}=    Create List    ${9}
        | ${param values}    ${result sets}=    Call Stored Procedure    return_out_param_without_result_sets
        | ...    ${params}    additional_output_params=${out_params}
        | # ${result sets} = []
        | # ${param values} = ('give me 1', 1)

        The library uses the sample values in the `additional_output_params` list to determine the number and the type
        of OUT parameters - so they are type-sensitive, the type must be the same as in the procedure itself.

        === MS SQL procedure returning a result set (no OUT params) ===
        If a procedure doesn't have any OUT params and returns only result sets, they are handled in a normal way.
        Consider the following procedure:
        | CREATE PROCEDURE get_all_first_and_second_names
        | AS
        | BEGIN
        |   SELECT FIRST_NAME FROM person;
        |   SELECT LAST_NAME FROM person;
        |   RETURN;
        | END;

        Calling the procedure in Robot Framework:
        | ${param values}    ${result sets}=    Call Stored Procedure    get_all_first_and_second_names
        | ${param values} = ()
        | ${result sets} = [[('Franz Allan',), ('Jerry',)], [('See',), ('Schneider',)]]

        === MS SQL procedure returning result sets AND OUT params ===
        This case is *not fully supported* by the library - the OUT params won't be fetched.
        """
        db_connection = self.connection_store.get_connection(alias)
        if procedure_params is None:
            procedure_params = []
        if additional_output_params is None:
            additional_output_params = []
        cur = None
        try:
            if db_connection.module_name == "pymssql":
                cur = db_connection.client.cursor(as_dict=False)
            else:
                cur = db_connection.client.cursor()

            param_values = []
            result_sets = []

            if db_connection.module_name == "pymysql":
                cur.callproc(procedure_name, procedure_params)

                # first proceed the result sets if available
                result_sets_available = True
                while result_sets_available:
                    result_sets.append(list(cur.fetchall()))
                    result_sets_available = cur.nextset()
                # last result set is always empty
                # https://pymysql.readthedocs.io/en/latest/modules/cursors.html#pymysql.cursors.Cursor.callproc
                result_sets.pop()

                # now go on with single values - modified input params
                for i in range(0, len(procedure_params)):
                    cur.execute(f"select @_{procedure_name}_{i}")
                    param_values.append(cur.fetchall()[0][0])

            elif db_connection.module_name in ["oracledb", "cx_Oracle"]:
                # check if "CURSOR" params were passed - they will be replaced
                # with cursor variables for storing the result sets
                params_substituted = procedure_params.copy()
                cursor_params = []
                for i in range(0, len(procedure_params)):
                    if procedure_params[i] == "CURSOR":
                        cursor_param = db_connection.client.cursor()
                        params_substituted[i] = cursor_param
                        cursor_params.append(cursor_param)
                param_values = cur.callproc(procedure_name, params_substituted)
                for result_set in cursor_params:
                    result_sets.append(list(result_set))

            elif db_connection.module_name in ["psycopg2", "psycopg3"]:
                # check if "CURSOR" params were passed - they will be replaced
                # with cursor variables for storing the result sets
                params_substituted = procedure_params.copy()
                cursor_params = []
                for i in range(0, len(procedure_params)):
                    if procedure_params[i] == "CURSOR":
                        cursor_param = f"CURSOR_{i}"
                        params_substituted[i] = cursor_param
                        cursor_params.append(cursor_param)
                param_values = cur.callproc(procedure_name, params_substituted)
                if cursor_params:
                    for cursor_param in cursor_params:
                        cur.execute(f'FETCH ALL IN "{cursor_param}"')
                        result_set = cur.fetchall()
                        result_sets.append(list(result_set))
                else:
                    if db_connection.module_name in ["psycopg3"]:
                        result_sets_available = True
                        while result_sets_available:
                            result_sets.append(list(cur.fetchall()))
                            result_sets_available = cur.nextset()
                    else:
                        result_set = cur.fetchall()
                        result_sets.append(list(result_set))

            else:
                if db_connection.module_name == "pymssql":
                    mssql = importlib.import_module("pymssql")
                    procedure_params = procedure_params.copy()
                    for param in additional_output_params:
                        procedure_params.append(mssql.output(type(param), param))

                else:
                    logger.info(
                        f"Calling a stored procedure for '{db_connection.module_name}'. "
                        "No special handling is known, so trying the common way with return params and result sets."
                    )

                param_values = cur.callproc(procedure_name, procedure_params)
                logger.info("Reading the procedure result sets..")
                result_sets_available = True
                while result_sets_available:
                    result_set = []
                    for row in cur:
                        result_set.append(row)
                    if result_set:
                        result_sets.append(list(result_set))
                    if hasattr(cur, "nextset") and inspect.isroutine(cur.nextset):
                        result_sets_available = cur.nextset()
                    else:
                        result_sets_available = False

            self._commit_if_needed(db_connection, no_transaction)
            return param_values, result_sets
        except Exception as e:
            self._rollback_and_raise(db_connection, no_transaction, e)

    def set_logging_query_results(self, enabled: Optional[bool] = None, log_head: Optional[int] = None):
        """
        Allows to enable/disable logging of query results and to adjust the log head value.
        - Overrides the values, which were set during the library import.
        - See `Logging query results` for details.

        Examples:
        | Set Logging Query Results | enabled=False |
        | Set Logging Query Results | enabled=True | log_head=0 |
        | Set Logging Query Results | log_head=10 |
        """
        if enabled is not None:
            self.LOG_QUERY_RESULTS = enabled
        if log_head is not None:
            if log_head < 0:
                raise ValueError(f"Wrong log head value provided: {log_head}. The value can't be negative!")
            self.LOG_QUERY_RESULTS_HEAD = log_head

    def _execute_sql(
        self,
        cur,
        sql_statement: str,
        omit_trailing_semicolon: Optional[bool] = False,
        parameters: Optional[Tuple] = None,
        replace_robot_variables=False,
    ):
        """
        Runs the `sql_statement` using `cur` as Cursor object.

        Use `omit_trailing_semicolon` parameter (bool) for explicit instruction,
        if the trailing semicolon (;) should be removed - otherwise the statement
        won't be executed by some databases (e.g. Oracle).
        Otherwise, it's decided based on the current database module in use.
        """
        if omit_trailing_semicolon:
            sql_statement = sql_statement.rstrip(";")
        if replace_robot_variables:
            sql_statement = BuiltIn().replace_variables(sql_statement)
        if parameters is None:
            logger.info(f'Executing sql:<br><code style="font-weight: bold;">{sql_statement}</code>', html=True)
            return cur.execute(sql_statement)
        else:
            logger.info(
                f'Executing sql:<br><code style="font-weight: bold;">{sql_statement}</code><br>Parameters: <code style="font-weight: bold;">{parameters}</code>',
                html=True,
            )
            return cur.execute(sql_statement, parameters)

    def _commit_if_needed(self, db_connection: Connection, no_transaction):
        if no_transaction:
            logger.info(f"Perform no commit, because 'no_transaction' set to {no_transaction}")
        else:
            logger.info("Commit the transaction")
            db_connection.client.commit()

    def _rollback_and_raise(self, db_connection: Connection, no_transaction, e):
        logger.info(f"Error occurred: {e}")
        if no_transaction:
            logger.info(f"Perform no rollback, because 'no_transaction' set to {no_transaction}")
        else:
            logger.info("Rollback the transaction")
            db_connection.client.rollback()
        raise e

    def _log_query_results(self, col_names, result_rows, log_head: Optional[int] = None):
        """
        Logs the `result_rows` of a query in RF log as a HTML table.
        The `col_names` are needed for the table header.
        Max. `log_head` rows are logged (`0` disables the limit).
        """
        if not self.LOG_QUERY_RESULTS:
            return

        if log_head is None:
            log_head = self.LOG_QUERY_RESULTS_HEAD

        if result_rows is None:
            result_rows = []

        cell_border_and_align = "border: 1px solid rgb(160 160 160);padding: 8px 10px;text-align: center;"
        table_border = "2px solid rgb(140 140 140)"
        row_index_background_color = "#d6ecd4"
        row_index_text_color = "black"
        msg = '<div style="max-width: 100%; overflow-x: auto;">'
        msg += f'<table style="width: auto; border-collapse: collapse; border: {table_border}">'
        msg += f'<caption style="text-align: left; font-weight: bold; padding: 5px;">Query returned {len(result_rows)} rows</caption>'
        msg += "<tr>"
        msg += f'<th scope="col" style="color:{row_index_text_color}; background-color: {row_index_background_color}; {cell_border_and_align}">Row</th>'
        for col in col_names:
            msg += f'<th scope="col" style="background-color: #505050; color: #fff;{cell_border_and_align}">{col}</th>'
        msg += "</tr>"
        table_truncated = False
        for i, row in enumerate(result_rows):
            if log_head and i >= log_head:
                table_truncated = True
                break
            row_style = ""
            if i % 2 == 0:
                row_style = ' style="background-color: var(--secondary-color, #eee)"'
            msg += f"<tr{row_style}>"
            msg += f'<th scope="row" style="color:{row_index_text_color}; background-color: {row_index_background_color};{cell_border_and_align}">{i}</th>'
            for cell in row:
                try:
                    cell_string = str(cell)
                except TypeError as e:
                    cell_string = f"Unable printing the value: {e}"
                msg += f'<td style="{cell_border_and_align}">{cell_string}</td>'
            msg += "</tr>"
        msg += "</table>"
        if table_truncated:
            msg += (
                f'<p style="font-weight: bold;">Log limit of {log_head} rows was reached, the table was truncated</p>'
            )
        msg += "</div>"
        logger.info(msg, html=True)
