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

import inspect
import re
import sys
from typing import List, Optional, Tuple

from robot.api import logger


class Query:
    """
    Query handles all the querying done by the Database Library.
    """

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
            logger.info(f"Executing : Query  |  {selectStatement} ")
            self.__execute_sql(cur, selectStatement, parameters=parameters)
            all_rows = cur.fetchall()
            if returnAsDict:
                col_names = [c[0] for c in cur.description]
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
            logger.info(f"Executing : Row Count  |  {selectStatement}")
            self.__execute_sql(cur, selectStatement, parameters=parameters)
            data = cur.fetchall()
            if db_connection.module_name in ["sqlite3", "ibm_db", "ibm_db_dbi", "pyodbc"]:
                return len(data)
            return cur.rowcount
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
            logger.info("Executing : Description  |  {selectStatement}")
            self.__execute_sql(cur, selectStatement, parameters=parameters)
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
            logger.info(f"Executing : Delete All Rows From Table  |  {query}")
            result = self.__execute_sql(cur, query)
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
                logger.info(f"Executing : Execute SQL Script  |  {sqlScriptFileName}")
                if not split:
                    logger.info("Statements splitting disabled - pass entire script content to the database module")
                    self.__execute_sql(cur, sql_file.read())
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
                        logger.info(f"Executing statement from script file: {statement}")
                        line_ends_with_proc_end = re.compile(r"(\s|;)" + proc_end_pattern.pattern + "$")
                        omit_semicolon = not line_ends_with_proc_end.search(statement.lower())
                        self.__execute_sql(cur, statement, omit_semicolon)
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
            logger.info(f"Executing : Execute SQL String  |  {sqlString}")
            self.__execute_sql(cur, sqlString, omit_trailing_semicolon=omitTrailingSemicolon, parameters=parameters)
            if not sansTran:
                db_connection.client.commit()
        finally:
            if cur and not sansTran:
                db_connection.client.rollback()

    def call_stored_procedure(
        self, spName: str, spParams: Optional[List[str]] = None, sansTran: bool = False, alias: Optional[str] = None
    ):
        """
        Calls a stored procedure `spName` with the `spParams` - a *list* of parameters the procedure requires.
        Use the special *CURSOR* value for OUT params, which should receive result sets -
        they will be converted to appropriate DB variables before calling the procedure.
        This is necessary only for some databases (e.g. Oracle or PostgreSQL).

        The keywords always *returns two lists*:
        - *Param values* - the copy of procedure parameters (modified, if the procedure changes the OUT params).
        The list is empty, if procedures receives no params.
        - *Result sets* - the list of lists, each of them containing results of some query, if the procedure
        returns them or put them in the OUT params of type *CURSOR* (like in Oracle or PostgreSQL).

        It also depends on the database, how the procedure returns the values - as params or as result sets.
        E.g. calling a procedure in *PostgreSQL* returns even a single value of an OUT param as a result set.

        Simple example:
        | @{Params} = | Create List | Jerry | out_second_name |
        | @{Param values}    @{Result sets} = | Call Stored Procedure | Get_second_name | ${Params} |
        | # ${Param values} = ['Jerry', 'Schneider'] |
        | # ${result sets} = [] |

        Example with a single CURSOR parameter (Oracle DB):
        | @{Params} = | Create List | CURSOR |
        | @{Param values}    @{Result sets} = | Call Stored Procedure | Get_all_second_names | ${Params} |
        | # ${Param values} = [<oracledb.Cursor on <oracledb.Connection ...>>] |
        | # ${result sets} = [[('See',), ('Schneider',)]] |

        Example with multiple CURSOR parameters (Oracle DB):
        | @{Params} = | Create List | CURSOR | CURSOR |
        | @{Param values}    @{Result sets} = | Call Stored Procedure | Get_all_first_and_second_names | ${Params} |
        | # ${Param values} = [<oracledb.Cursor on <oracledb.Connection ...>>, <oracledb.Cursor on <oracledb.Connection ...>>] |
        | # ${result sets} = [[('Franz Allan',), ('Jerry',)], [('See',), ('Schneider',)]] |

        Use optional ``alias`` parameter to specify what connection should be used for the query if you have more
        than one connection open.

        Use optional `sansTran` to run command without an explicit transaction commit or rollback:
        | @{Param values}    @{Result sets} = | Call Stored Procedure | DBName.SchemaName.StoredProcName | ${Params} | True |
        """
        db_connection = self.connection_store.get_connection(alias)
        if spParams is None:
            spParams = []
        cur = None
        try:
            logger.info(f"Executing : Call Stored Procedure  |  {spName}  |  {spParams}")
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
                cur = db_connection.client.cursor()
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
                logger.info(
                    f"CAUTION! Calling a stored procedure for '{db_connection.module_name}' is not tested, "
                    "results might be invalid!"
                )
                cur = db_connection.client.cursor()
                param_values = cur.callproc(spName, spParams)
                logger.info("Reading the procedure results..")
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

    def __execute_sql(
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
            logger.debug(f"Executing sql '{sql_statement}' without parameters")
            return cur.execute(sql_statement)
        else:
            logger.debug(f"Executing sql '{sql_statement}' with parameters: {parameters}")
            return cur.execute(sql_statement, parameters)
