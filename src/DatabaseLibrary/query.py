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

from robot.api import logger


class Query:
    """
    Query handles all the querying done by the Database Library.
    """

    def __init__(self, log_query_results, log_query_results_head):
        self.LOG_QUERY_RESULTS = log_query_results
        self.LOG_QUERY_RESULTS_HEAD = log_query_results_head

    def query(
        self,
        selectStatement: str,
        sansTran: bool = False,
        returnAsDict: bool = False,
        alias: Optional[str] = None,
        parameters: Optional[Tuple] = None,
    ):
        """
        Runs a query with the ``selectStatement`` and returns the result as a list of rows.
        The type of row values depends on the database module -
        usually they are tuples or tuple-like objects.

        Set optional input ``returnAsDict`` to _True_ to explicitely convert the return values
        into a list of dictionaries.

        Use optional ``alias`` parameter to specify what connection should be used for the query if you have more
        than one connection open.

        Use optional ``parameters`` for query variable substitution (variable substitution syntax may be different
        depending on the database client):
        | @{parameters} | Create List |  person |
        | Query | SELECT * FROM %s | parameters=${parameters} |

        Use optional ``sansTran`` to run command without an explicit transaction commit or rollback:
        | @{queryResults} | Query | SELECT * FROM person | True |

        Tip: Unless you want to log all column values of the specified rows,
        try specifying the column names in your select statements
        as much as possible to prevent any unnecessary surprises with schema
        changes and to easily see what your [] indexing is trying to retrieve
        (i.e. instead of `"select * from my_table"`, try
        `"select id, col_1, col_2 from my_table"`).

        For example, given we have a table `person` with the following data:
        | id | first_name  | last_name |
        |  1 | Franz Allan | See       |

        When you do the following:
        | @{queryResults} | Query | SELECT * FROM person |
        | @{queryResults} | Query | SELECT * FROM person | alias=my_alias |
        | Log Many | @{queryResults} |

        You will get the following:
        [1, 'Franz Allan', 'See']

        Also, you can do something like this:
        | ${queryResults} | Query | SELECT first_name, last_name FROM person |
        | Log | ${queryResults[0][1]}, ${queryResults[0][0]} |

        And get the following
        See, Franz Allan
        """
        db_connection = self.connection_store.get_connection(alias)
        cur = None
        try:
            cur = db_connection.client.cursor()
            self._execute_sql(cur, selectStatement, parameters=parameters)
            all_rows = cur.fetchall()
            col_names = [c[0] for c in cur.description]
            self._log_query_results(col_names, all_rows)
            if returnAsDict:
                return [dict(zip(col_names, row)) for row in all_rows]
            return all_rows
        finally:
            if cur and not sansTran:
                db_connection.client.rollback()

    def row_count(
        self,
        selectStatement: str,
        sansTran: bool = False,
        alias: Optional[str] = None,
        parameters: Optional[Tuple] = None,
    ):
        """
        Uses the input ``selectStatement`` to query the database and returns the number of rows from the query.

        Use optional ``alias`` parameter to specify what connection should be used for the query if you have more
        than one connection open.

        Use optional ``sansTran`` to run command without an explicit transaction commit or rollback:

        Use optional ``parameters`` for query variable substitution (variable substitution syntax may be different
        depending on the database client):

        Examples:
        | ${rowCount} | Row Count | SELECT * FROM person |
        | ${rowCount} | Row Count | SELECT * FROM person | sansTran=True |
        | ${rowCount} | Row Count | SELECT * FROM person | alias=my_alias |
        | @{parameters} | Create List |  person |
        | ${rowCount} | Row Count | SELECT * FROM %s | parameters=${parameters} |
        """
        db_connection = self.connection_store.get_connection(alias)
        cur = None
        try:
            cur = db_connection.client.cursor()
            self._execute_sql(cur, selectStatement, parameters=parameters)
            data = cur.fetchall()
            col_names = [c[0] for c in cur.description]
            if db_connection.module_name in ["sqlite3", "ibm_db", "ibm_db_dbi", "pyodbc"]:
                current_row_count = len(data)
            else:
                current_row_count = cur.rowcount
            logger.info(f"Retrieved {current_row_count} rows")
            self._log_query_results(col_names, data)
            return current_row_count
        finally:
            if cur and not sansTran:
                db_connection.client.rollback()

    def description(
        self,
        selectStatement: str,
        sansTran: bool = False,
        alias: Optional[str] = None,
        parameters: Optional[Tuple] = None,
    ):
        """
        Uses the input ``selectStatement`` to query a table in the db which will be used to determine the description.

        For example, given we have a table `person` with the following data:
        | id | first_name  | last_name |
        |  1 | Franz Allan | See       |

        When you do the following:
        | @{queryResults} | Description | SELECT * FROM person |
        | @{queryResults} | Description | SELECT * FROM person | alias=my_alias |
        | Log Many | @{queryResults} |

        You will get the following:
        [Column(name='id', type_code=1043, display_size=None, internal_size=255, precision=None, scale=None, null_ok=None)]
        [Column(name='first_name', type_code=1043, display_size=None, internal_size=255, precision=None, scale=None, null_ok=None)]
        [Column(name='last_name', type_code=1043, display_size=None, internal_size=255, precision=None, scale=None, null_ok=None)]

        Use optional ``alias`` parameter to specify what connection should be used for the query if you have more
        than one connection open.

        Use optional ``parameters`` for query variable substitution (variable substitution syntax may be different
        depending on the database client):
        | @{parameters} | Create List |  person |
        | ${desc} | Description | SELECT * FROM %s | parameters=${parameters} |

        Using optional `sansTran` to run command without an explicit transaction commit or rollback:
        | @{queryResults} | Description | SELECT * FROM person | True |
        """
        db_connection = self.connection_store.get_connection(alias)
        cur = None
        try:
            cur = db_connection.client.cursor()
            self._execute_sql(cur, selectStatement, parameters=parameters)
            description = list(cur.description)
            if sys.version_info[0] < 3:
                for row in range(0, len(description)):
                    description[row] = (description[row][0].encode("utf-8"),) + description[row][1:]
            return description
        finally:
            if cur and not sansTran:
                db_connection.client.rollback()

    def delete_all_rows_from_table(self, tableName: str, sansTran: bool = False, alias: Optional[str] = None):
        """
        Delete all the rows within a given table.

        Use optional `sansTran` to run command without an explicit transaction commit or rollback.

        Use optional ``alias`` parameter to specify what connection should be used for the query if you have more
        than one connection open.

        Examples:
        | Delete All Rows From Table | person |
        | Delete All Rows From Table | person | alias=my_alias |
        | Delete All Rows From Table | person | sansTran=True |
        """
        db_connection = self.connection_store.get_connection(alias)
        cur = None
        query = f"DELETE FROM {tableName}"
        try:
            cur = db_connection.client.cursor()
            result = self._execute_sql(cur, query)
            if result is not None:
                if not sansTran:
                    db_connection.client.commit()
                return result
            if not sansTran:
                db_connection.client.commit()
        finally:
            if cur and not sansTran:
                db_connection.client.rollback()

    def execute_sql_script(
        self, sqlScriptFileName: str, sansTran: bool = False, alias: Optional[str] = None, split: bool = True
    ):
        """
        Executes the content of the `sqlScriptFileName` as SQL commands. Useful for setting the database to a known
        state before running your tests, or clearing out your test data after running each a test.

        SQL commands are expected to be delimited by a semicolon (';') - they will be split and executed separately.
        You can disable this behaviour setting the parameter `split` to _False_ -
        in this case the entire script content will be passed to the database module for execution.

        Sample usage :
        | Execute Sql Script | ${EXECDIR}${/}resources${/}DDL-setup.sql |
        | Execute Sql Script | ${EXECDIR}${/}resources${/}DML-setup.sql |
        | Execute Sql Script | ${EXECDIR}${/}resources${/}DDL-setup.sql | alias=my_alias |
        | #interesting stuff here |
        | Execute Sql Script | ${EXECDIR}${/}resources${/}DML-teardown.sql |
        | Execute Sql Script | ${EXECDIR}${/}resources${/}DDL-teardown.sql |


        For example:
        DELETE FROM person_employee_table;
        DELETE FROM person_table;
        DELETE FROM employee_table;

        Also, the last SQL command can optionally omit its trailing semi-colon.

        For example:
        DELETE FROM person_employee_table;
        DELETE FROM person_table;
        DELETE FROM employee_table

        Given this, that means you can create spread your SQL commands in several
        lines.

        For example:
        DELETE
          FROM person_employee_table;
        DELETE
          FROM person_table;
        DELETE
          FROM employee_table

        However, lines that starts with a number sign (`#`) or a double dash ("--")
        are treated as a commented line. Thus, none of the contents of that line will be executed.


        For example:
        # Delete the bridging table first...
        DELETE
          FROM person_employee_table;
          # ...and then the bridged tables.
        DELETE
          FROM person_table;
        DELETE
          FROM employee_table

        The slash signs ("/") are always ignored and have no impact on execution order.

        Use optional ``alias`` parameter to specify what connection should be used for the query if you have more
        than one connection open.

        Use optional `sansTran` to run command without an explicit transaction commit or rollback:
        | Execute Sql Script | ${EXECDIR}${/}resources${/}DDL-setup.sql | True |
        """
        db_connection = self.connection_store.get_connection(alias)
        with open(sqlScriptFileName, encoding="UTF-8") as sql_file:
            cur = None
            try:
                cur = db_connection.client.cursor()
                if not split:
                    logger.info("Statements splitting disabled - pass entire script content to the database module")
                    self._execute_sql(cur, sql_file.read())
                else:
                    logger.info("Splitting script file into statements...")
                    statements_to_execute = []
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
                            quotes -= sqlFragment.count("''")
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

                    for statement in statements_to_execute:
                        line_ends_with_proc_end = re.compile(r"(\s|;)" + proc_end_pattern.pattern + "$")
                        omit_semicolon = not line_ends_with_proc_end.search(statement.lower())
                        self._execute_sql(cur, statement, omit_semicolon)
                if not sansTran:
                    db_connection.client.commit()
            finally:
                if cur and not sansTran:
                    db_connection.client.rollback()

    def execute_sql_string(
        self,
        sqlString: str,
        sansTran: bool = False,
        alias: Optional[str] = None,
        parameters: Optional[Tuple] = None,
        omitTrailingSemicolon: Optional[bool] = None,
    ):
        """
        Executes the ``sqlString`` as a single SQL command.

        Use optional ``sansTran`` to run command without an explicit transaction commit or rollback.

        Use optional ``omitTrailingSemicolon`` parameter for explicit instruction,
        if the trailing semicolon (;) at the SQL string end should be removed or not:
        - Some database modules (e.g. Oracle) throw an exception, if you leave a semicolon at the string end
        - However, there are exceptional cases, when you need it even for Oracle - e.g. at the end of a PL/SQL block.
        - If not specified, it's decided based on the current database module in use. For Oracle, the semicolon is removed by default.

        Use optional ``alias`` parameter to specify what connection should be used for the query if you have more
        than one connection open.

        Use optional ``parameters`` for query variable substitution (variable substitution syntax may be different
        depending on the database client).

        For example:
        | Execute Sql String | DELETE FROM person_employee_table; DELETE FROM person_table |
        | Execute Sql String | DELETE FROM person_employee_table; DELETE FROM person_table | alias=my_alias |
        | Execute Sql String | DELETE FROM person_employee_table; DELETE FROM person_table | sansTran=True |
        | Execute Sql String | CREATE PROCEDURE proc AS BEGIN DBMS_OUTPUT.PUT_LINE('Hello!'); END; | omitTrailingSemicolon=False |
        | @{parameters} | Create List |  person_employee_table |
        | Execute Sql String | SELECT * FROM %s | parameters=${parameters} |
        """
        db_connection = self.connection_store.get_connection(alias)
        cur = None
        try:
            cur = db_connection.client.cursor()
            self._execute_sql(cur, sqlString, omit_trailing_semicolon=omitTrailingSemicolon, parameters=parameters)
            if not sansTran:
                db_connection.client.commit()
        finally:
            if cur and not sansTran:
                db_connection.client.rollback()

    def call_stored_procedure(
        self,
        spName: str,
        spParams: Optional[List] = None,
        sansTran: bool = False,
        alias: Optional[str] = None,
        additional_output_params: Optional[List] = None,
    ):
        """
        Calls a stored procedure `spName` with the `spParams` - a *list* of parameters the procedure requires.
        *Returns two lists* - the _parameter values_ and the _result sets_.

        Use the special *CURSOR* value for OUT params, which should receive result sets - relevant only for some databases (e.g. Oracle or PostgreSQL).

        Use the `additional_output_params` list for OUT params of a procedure in MSSQL.

        Use optional ``alias`` parameter to specify what connection should be used for the query if you have more
        than one connection open.

        Use optional `sansTran` to run command without an explicit transaction commit or rollback.

        = Handling parameters and result sets =
        Handling the input and output parameters and the result sets is very different
        depending on the database itself and on the Python database driver - i.e. how it implements the `cursor.callproc()` function.

        == Common case (e.g. MySQL) ==
        Generally a procedure call requires all parameter values (IN and OUT) put together in a list - `spParams`.

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

        Calling the procedure in Robot Framework requires putting the IN parameters as usual in the `spParams` argument,
        but the sample values of OUT parameters must be put in the argument `additional_output_params`.

        | @{params}=    Create List    give me 1
        | @{out_params}=    Create List    ${9}
        | ${param values}    ${result sets}=    Call Stored Procedure    return_out_param_without_result_sets
        | ...    ${params}    additional_output_params=${out_params}
        | # ${result sets} = [[('Franz Allan',), ('Jerry',)], [('See',), ('Schneider',)]]
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
        if spParams is None:
            spParams = []
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
                cur.callproc(spName, spParams)

                # first proceed the result sets if available
                result_sets_available = True
                while result_sets_available:
                    result_sets.append(list(cur.fetchall()))
                    result_sets_available = cur.nextset()
                # last result set is always empty
                # https://pymysql.readthedocs.io/en/latest/modules/cursors.html#pymysql.cursors.Cursor.callproc
                result_sets.pop()

                # now go on with single values - modified input params
                for i in range(0, len(spParams)):
                    cur.execute(f"select @_{spName}_{i}")
                    param_values.append(cur.fetchall()[0][0])

            elif db_connection.module_name in ["oracledb", "cx_Oracle"]:
                # check if "CURSOR" params were passed - they will be replaced
                # with cursor variables for storing the result sets
                params_substituted = spParams.copy()
                cursor_params = []
                for i in range(0, len(spParams)):
                    if spParams[i] == "CURSOR":
                        cursor_param = db_connection.client.cursor()
                        params_substituted[i] = cursor_param
                        cursor_params.append(cursor_param)
                param_values = cur.callproc(spName, params_substituted)
                for result_set in cursor_params:
                    result_sets.append(list(result_set))

            elif db_connection.module_name in ["psycopg2", "psycopg3"]:
                # check if "CURSOR" params were passed - they will be replaced
                # with cursor variables for storing the result sets
                params_substituted = spParams.copy()
                cursor_params = []
                for i in range(0, len(spParams)):
                    if spParams[i] == "CURSOR":
                        cursor_param = f"CURSOR_{i}"
                        params_substituted[i] = cursor_param
                        cursor_params.append(cursor_param)
                param_values = cur.callproc(spName, params_substituted)
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
                    spParams = spParams.copy()
                    for param in additional_output_params:
                        spParams.append(mssql.output(type(param), param))

                else:
                    logger.info(
                        f"Calling a stored procedure for '{db_connection.module_name}'. "
                        "No special handling is known, so trying the common way with return params and result sets."
                    )

                param_values = cur.callproc(spName, spParams)
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

            if not sansTran:
                db_connection.client.commit()

            return param_values, result_sets
        finally:
            if cur and not sansTran:
                db_connection.client.rollback()

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
        omit_trailing_semicolon: Optional[bool] = None,
        parameters: Optional[Tuple] = None,
    ):
        """
        Runs the `sql_statement` using `cur` as Cursor object.
        Use `omit_trailing_semicolon` parameter (bool) for explicit instruction,
        if the trailing semicolon (;) should be removed - otherwise the statement
        won't be executed by some databases (e.g. Oracle).
        Otherwise, it's decided based on the current database module in use.
        """
        if omit_trailing_semicolon is None:
            omit_trailing_semicolon = self.omit_trailing_semicolon
        if omit_trailing_semicolon:
            sql_statement = sql_statement.rstrip(";")
        if parameters is None:
            logger.info(f'Executing sql:<br><code style="font-weight: bold;">{sql_statement}</code>', html=True)
            return cur.execute(sql_statement)
        else:
            logger.info(
                f'Executing sql:<br><code style="font-weight: bold;">{sql_statement}</code><br>Parameters: <code style="font-weight: bold;">{parameters}</code>',
                html=True,
            )
            return cur.execute(sql_statement, parameters)

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
        cell_border_and_align = "border: 1px solid rgb(160 160 160);padding: 8px 10px;text-align: center;"
        table_border = "2px solid rgb(140 140 140)"
        row_index_color = "#d6ecd4"
        msg = f'<div style="max-width: 100%; overflow-x: auto;">'
        msg += f'<table style="width: auto; border-collapse: collapse; border: {table_border}">'
        msg += f'<caption style="text-align: left; font-weight: bold; padding: 5px;">Query returned {len(result_rows)} rows</caption>'
        msg += "<tr>"
        msg += f'<th scope="col" style="background-color: {row_index_color}; {cell_border_and_align}">Row</th>'
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
                row_style = ' style="background-color: #eee;"'
            msg += f"<tr{row_style}>"
            msg += f'<th scope="row" style="background-color: {row_index_color};{cell_border_and_align}">{i}</th>'
            for cell in row:
                msg += f'<td style="{cell_border_and_align}">{cell}</td>'
            msg += "</tr>"
        msg += "</table>"
        if table_truncated:
            msg += (
                f'<p style="font-weight: bold;">Log limit of {log_head} rows was reached, the table was truncated</p>'
            )
        msg += "</div>"
        logger.info(msg, html=True)
