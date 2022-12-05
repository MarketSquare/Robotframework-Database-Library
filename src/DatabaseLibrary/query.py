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

import os
from operator import eq, ge, gt, le, lt
from typing import Any, Dict, List, Optional, Union

from func_timeout import FunctionTimedOut, func_set_timeout
from robot.api import logger
from robot.api.deco import keyword, not_keyword
from robot.libraries.Collections import Collections

from .exceptions import TechnicalTestFailure, TestFailure

# how do we understand the operators
semantics = {
    le: ("at most"),
    ge: ("at least"),
    eq: ("exactly"),
    lt: ("less than"),
    gt: ("more than"),
}

# need an instance to log list
cl = Collections()


class Query:
    """
    Query handles all the querying done by the Database Library.
    """

    @not_keyword
    def asserted_query(
        self, select_statement: str, reference_count: int, op: Union[le, ge, eq, lt, gt]
    ) -> None:
        """Executes a select statement and asserts whether there are as many results as expected with given comparison operator.

        Args:
            select_statement (str): SQL Select Statement.
            reference_count (int): what's the frame of reference for the returned size?
            op (Union[le, ge, eq, lt, gt]): what operator should be used for comparison (lesser, greater, equal, greaterequal, lesserequal)

        Raises:
            TestFailure: the count does not fit the operator + reference count
            TechnicalTestFailure: Reraises errors caught in the underlying functions with more details.
            TechnicalTestFailure: Raised in case of unexpected errors.
            FunctionTimedOut: Raises if execute_sql times out (1 hour)

        """
        cur = None
        step = ""
        logger.info(f"Executing: Query | {select_statement}")
        try:
            step = "Getting cursor"
            cur = self._dbconnection.cursor()

            step = "Executing SQL statement"
            self.execute_sql(cur, select_statement)

            # only fetch however many we need to make a positive verification
            logger.debug(
                f"Initial fetch will be limited to {reference_count + 1} records.")
            step = f"Fetch {reference_count + 1} records."
            rows = cur.fetchmany(reference_count + 1)

            step = "Get result size"
            actual_length = len(rows) if rows else 0

            step = "Compare expected to actual"
            if not op(actual_length, reference_count):
                # fetching one by one to keep the memory usage low as the rows can be super wide sometimes.
                while True:
                    step = f"Fetch next row. Currently {actual_length} rows fetched."
                    if not cur.fetchone():
                        # if no more elements, break the loop and raise the test failure
                        break
                    # count how many there are
                    actual_length += 1
                raise TestFailure(
                    f"Query returned {actual_length} rows but test expected {semantics[op]} {reference_count}."
                )
        except TestFailure:
            raise
        except TechnicalTestFailure as ttf:
            raise TechnicalTestFailure(
                f"Asserted query failed. \nStep: {step}. \nDetails: {str(ttf)}") from ttf
        except FunctionTimedOut:
            raise
        except Exception as ex:
            raise TechnicalTestFailure(
                f"Asserted query failed with unexpected error. \nStep: {step}. \nDetails: {str(ex)}") from ex

        finally:
            self._cursor_cleanup(cur)

    @keyword(name="Query")
    def query(self, select_statement: str) -> List[Dict]:
        """Execute a select statement and return the results as a list of dictionaries

        Args:
            select_statement (str): SQL Select statement

        Raises:
            TechnicalTestFailure: Reraises errors caught in the underlying functions with more details.
            TechnicalTestFailure: Raised in case of unexpected errors.
            FunctionTimedOut: Raises if execute_sql times out (1 hour)

        Returns:
            List[Dict]: results of the query as list of dictionaries
        """
        cur = None
        logger.info(f"Executing: Query | {select_statement}")
        limit = os.environ.get("QUERY_LIMIT", None)
        try:
            step = "Create a cursor on the database connection."
            cur = self._dbconnection.cursor()

            if limit:
                step = f"Setting limit query limit"
                logger.debug(f"Query will be limited to {limit} records.")
                limit = int(limit)

            step = f"Executing SQL statement"
            self.execute_sql(cur, select_statement)

            step = f"Fetching {limit or 'all'} rows"
            allRows = cur.fetchmany(limit) if limit else cur.fetchall()

            step = "Mapping rows from cursor description"
            mappedRows = []
            col_names = [c[0] for c in cur.description]

            step = "Mapping column names"
            for rowIdx in range(len(allRows)):
                d = {}
                for colIdx in range(len(allRows[rowIdx])):
                    d[col_names[colIdx]] = allRows[rowIdx][colIdx]
                mappedRows.append(d)
            cl.log_list(mappedRows)
            return mappedRows

        except TechnicalTestFailure as ttf:
            raise TechnicalTestFailure(
                f"Query failed \n Step: {step} because of error: {str(ttf)}") from ttf
        except FunctionTimedOut:
            raise
        except Exception as ex:
            raise TechnicalTestFailure(
                f"Query failed because of error: {str(ex)}") from ex
        finally:
            self._cursor_cleanup(cur)

    @keyword(name="Description")
    def description(self, select_statement: str) -> List[str]:
        """Perform a query and return its cursor's description

        Args:
            select_statement (str): SQL Statement

        Raises:
            TechnicalTestFailure: Reraises errors caught in the underlying functions with more details.
            TechnicalTestFailure: Raised in case of unexpected errors.
            FunctionTimedOut: Raises if execute_sql times out (1 hour)

        Returns:
            List[str]: list of strings describing the query results
        """
        cur = None
        logger.info(f"Executing: Description of {select_statement}")
        try:
            step = "Cursor creation"
            cur = self._dbconnection.cursor()

            step = "Cursor execution"
            self.execute_sql(cur, select_statement)

            step = "Get description from cursor"
            description = list(cur.description)
            return description
        except FunctionTimedOut:
            raise
        except TechnicalTestFailure as ttf:
            raise TechnicalTestFailure(
                f"Query failed \n Step: {step} because of error: {str(ttf)}") from ttf
        except Exception as ex:
            raise TechnicalTestFailure(
                f"SQL Script execution failed. \nStep: {step} \nDetails: {str(ex)}") from ex
        finally:
            self._cursor_cleanup(cur)

    @keyword(name="Execute SQL Script")
    @func_set_timeout(60 * 60)
    def execute_sql_script(self, sqlStatement: str, commit: bool = False, last_row_id: bool = False) -> Optional[int]:
        """Execute an SQL script.

        Args:
            sqlStatement (str): sql statement to execute
            commit (bool, optional): whether to commit the query results. Defaults to False.
            last_row_id (bool, optional): whether to return the last row id. Not supported by Snowflake. Defaults to False.

        Raises:
            TechnicalTestFailure: Reraises errors caught in the underlying functions with more details.
            TechnicalTestFailure: Raised in case of unexpected errors.
            FunctionTimedOut: Raises if execute_sql times out (1 hour)

        Returns:
            Optional[int]: the last row's id or None.
        """
        logger.info(f"Executing:  {sqlStatement}")
        step = ''
        try:
            step = "Cursor creation"
            cur = self._dbconnection.cursor()

            step = "Cursor execution"
            self.execute_sql(cur, sqlStatement)

            if commit:
                step = "Database commit"
                self._dbconnection.commit()

            if last_row_id:
                step = "Get the last row id from cursor"
                return cur.lastrowid

        except FunctionTimedOut:
            raise
        except Exception as ex:
            raise TechnicalTestFailure(
                f"SQL Script execution failed. \nStep: {step} \nDetails: {str(ex)}") from ex
        finally:
            self._cursor_cleanup(cur)

    @not_keyword
    @func_set_timeout(60 * 60)
    def execute_sql(self, cur, sqlStatement: str) -> Any:
        """Executes sql statement on a given cursor and returns results.

        Args:
            cur (dbapi2.cursor): a connected cursor compliant with dbapi2
            sqlStatement (str): sql statement to be executed

        Raises:
            TechnicalTestFailure: _description_
            TechnicalTestFailure: _description_
            TechnicalTestFailure: _description_

        Returns:
            Any: returns the results of the query
        """
        logger.info(f"Executing:  {sqlStatement}")
        try:
            return cur.execute(sqlStatement)
        except Exception as ex:
            ex_type_str = str(type(ex))
            if 'OperationalError' in ex_type_str:
                raise TechnicalTestFailure(
                    f"Test failed because of an Operational Error. \nThis might mean that a non-standard column type was encountered in a generic query. \nThis might mean you have used a non-existent column/table/schema. \nQuery: {sqlStatement} \nDetails: {str(ex)}") from ex
            elif 'ProgrammingError' in ex_type_str:
                raise TechnicalTestFailure(
                    f"Test failed because of a Programming Error. In most cases this is a syntax error in the query. Double check if the query executed is the intended query. \nQuery: {sqlStatement} \nDetails: {str(ex)}") from ex
            raise TechnicalTestFailure(
                f"Cursor execution failed \nQuery: {sqlStatement} \nDetails: {str(ex)}")

    @not_keyword
    def _cursor_cleanup(self, cur):
        try:
            if cur and self.db_api_module_name != 'databricks':
                self._dbconnection.rollback()
        except Exception as ex:
            logger.error(f"Error during cleanup: {ex}")
