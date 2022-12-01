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
from typing import Dict, List, Union

from exceptions import TechnicalTestFailure
from func_timeout import FunctionTimedOut, func_set_timeout
from robot.api import logger
from robot.api.deco import keyword, not_keyword
from robot.libraries.Collections import Collections

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
    def _cursor_cleanup(self, cur):
        try:
            if cur and self.db_api_module_name != 'databricks':
                self._dbconnection.rollback()
        except Exception as ex:
            logger.error(f"Error during cleanup: {ex}")

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
            AssertionError: the count does not fit the operator + reference count
        """
        cur = None
        logger.info(f"Executing: Query | {select_statement}")
        try:
            try:
                cur = self._dbconnection.cursor()
            except Exception as ex:
                raise TechnicalTestFailure(
                    f"Could not create a cursor on the connection because of error: {str(ex)} ")
            logger.debug(
                f"Initial fetch will be limited to {reference_count + 1} records.")
            try:
                self.execute_sql(cur, select_statement)
            except FunctionTimedOut:
                raise
            except Exception as ex:
                raise TechnicalTestFailure(
                    f"Could not execute asserted query because of error: {str(ex)}")
            try:
                # only fetch however many we need to make a positive verification
                rows = cur.fetchmany(reference_count + 1)
            except Exception as ex:
                raise TechnicalTestFailure(
                    f"Could not fetch {reference_count + 1} records from cursor because of error: {str(ex)}")
            try:
                actual_length = len(rows) if rows else 0
            except Exception as ex:
                raise TechnicalTestFailure(
                    f"Could not get the length of cursor result because of error: {str(ex)}")
            if not op(actual_length, reference_count):
                # fetching one by one to keep the memory usage low as the rows can be super wide sometimes.
                while True:
                    try:
                        if not cur.fetchone():
                            # if no more elements, break the loop and raise the assertion error
                            break
                    except Exception as ex:
                        raise TechnicalTestFailure(
                            f"Could not fetch next record from cursor because of error: {str(ex)}")
                    # count how many there are
                    actual_length += 1
                raise AssertionError(
                    f"Expected query to return {semantics[op]} {reference_count} rows, but got {actual_length}."
                )
        except TechnicalTestFailure as ttf:
            raise TechnicalTestFailure(
                f"Asserted query failed because of error: {str(ttf)}") from ttf
        except FunctionTimedOut:
            raise
        except Exception as ex:
            raise TechnicalTestFailure(
                f"Asserted query failed because of error: {str(ex)}") from ex

        finally:
            self._cursor_cleanup(cur)

    @keyword(name="Query")
    def query(self, select_statement: str) -> List[Dict]:
        """Execute a select statement and return the results as a list of dictionaries

        Args:
            select_statement (str): SQL Select statement

        Returns:
            List[Dict]: List of dictionaries (table rows)
        """
        cur = None
        logger.info(f"Executing: Query | {select_statement}")
        limit = os.environ.get("QUERY_LIMIT", None)
        try:
            try:
                cur = self._dbconnection.cursor()
            except Exception as ex:
                raise TechnicalTestFailure(
                    f"Could not create a cursor on the database connection because of error: {str(ex)}.")
            if limit:
                logger.debug(f"Query will be limited to {limit} records.")
                limit = int(limit)
            try:
                self.execute_sql(cur, select_statement)
            except FunctionTimedOut:
                raise
            except Exception as ex:
                raise TechnicalTestFailure(
                    f"Could not execute the query because of error: {str(ex)}.")
            try:
                allRows = cur.fetchmany(limit) if limit else cur.fetchall()
            except Exception as ex:
                raise TechnicalTestFailure(
                    f"Could not fetch the rows from cursor because of error: {str(ex)}")
            mappedRows = []
            try:
                col_names = [c[0] for c in cur.description]
            except Exception as ex:
                raise TechnicalTestFailure(
                    f"Could not fetch the column names from the cursor description because of error: {str(ex)}")

            for rowIdx in range(len(allRows)):
                d = {}
                try:
                    for colIdx in range(len(allRows[rowIdx])):
                        d[col_names[colIdx]] = allRows[rowIdx][colIdx]
                    mappedRows.append(d)
                except Exception as ex:
                    raise TechnicalTestFailure(
                        f"Could not map rows to columns because of error: {str(ex)}")
            cl.log_list(mappedRows)
            return mappedRows
        except TechnicalTestFailure as ttf:
            raise TechnicalTestFailure(
                f"Query failed because of error: {str(ttf)}") from ttf
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

        Returns:
            List[str]: list of strings describing the query results
        """
        cur = None
        logger.info(f"Executing: Description of {select_statement}")
        try:
            try:
                cur = self._dbconnection.cursor()
            except Exception as ex:
                raise TechnicalTestFailure from ex
            try:
                self.execute_sql(cur, select_statement)
            except FunctionTimedOut:
                raise
            except Exception as ttf:
                raise TechnicalTestFailure(
                    f"Execution sql failed because of {str(ex)}.")
            description = list(cur.description)
            return description
        except FunctionTimedOut:
            raise FunctionTimedOut
        except TechnicalTestFailure as ttf:
            raise TechnicalTestFailure(
                f"Description query failed because of error: {str(ttf)}") from ttf
        except Exception as ex:
            raise TechnicalTestFailure(
                f"Description query failed because of error: {str(ex)}") from ex
        finally:
            self._cursor_cleanup(cur)

    @keyword(name="Execute SQL Script")
    @func_set_timeout(60 * 60)
    def execute_sql_script(self, sqlStatement, commit=False, last_row_id=False):
        logger.info(f"Executing:  {sqlStatement}")
        try:
            try:
                cur = self._dbconnection.cursor()
            except Exception as ex:
                raise TechnicalTestFailure(
                    f"Cursor creation failed with error: {str(ex)}")
            try:
                cur.execute(sqlStatement)
            except Exception as ex:
                raise TechnicalTestFailure(
                    f"Cursor execution failed with error: {str(ex)}")
            if commit:
                try:
                    self._dbconnection.commit()
                except Exception as ex:
                    raise TechnicalTestFailure(
                        f"Commit failed with error: {str(ex)}.")
            if last_row_id:
                try:
                    return cur.lastrowid
                except Exception as ex:
                    raise TechnicalTestFailure(
                        f"Could not get the last row id from cursor with error: {str(ex)}.")
        except TechnicalTestFailure as ttf:
            raise TechnicalTestFailure(
                f"SQL Script execution failed with error: {str(ttf)}") from ttf
        except Exception as ex:
            raise TechnicalTestFailure(
                f"SQL Script execution failed with error: {str(ex)}") from ex

    @not_keyword
    @func_set_timeout(60 * 60)
    def execute_sql(self, cur, sqlStatement):
        logger.info(f"Executing:  {sqlStatement}")
        try:
            return cur.execute(sqlStatement)
        except Exception as ex:
            raise TechnicalTestFailure(
                f"Solo cursor execution step failed with: {str(ex)}")
