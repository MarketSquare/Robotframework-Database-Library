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
import sys
from operator import eq, ge, gt, le, lt
from typing import Dict, List, Union

from robot.api import logger
from robot.api.deco import keyword, not_keyword
from robot.libraries.Collections import Collections

# how do we understand the operators
semantics = {
    le: ('at most'),
    ge: ('at least'),
    eq: ('exactly'),
    lt: ('less than'),
    gt: ('more than')
}

# need an instance to log list
cl = Collections()


class Query:
    """
    Query handles all the querying done by the Database Library.
    """

    @not_keyword
    def asserted_query(self, select_statement: str, reference_count: int, op: Union[le, ge, eq, lt, gt]) -> None:
        """Executes a select statement and asserts whether there are as many results as expected with given comparison operator.

        Args:
            select_statement (str): SQL Select Statement.
            reference_count (int): what's the frame of reference for the returned size?
            op (Union[le, ge, eq, lt, gt]): what operator should be used for comparison (lesser, greater, equal, greaterequal, lesserequal)

        Raises:
            AssertionError: the count does not fit the operator + reference count
        """        
        cur = None
        try:
            cur = self._dbconnection.cursor()
            logger.info(f'Executing: Query | {select_statement}')
            logger.debug(f"Query will be limited to {reference_count + 1} records.")
            self.execute_sql(cur, select_statement)
            # only fetch however many we need to make a positive verification
            rows = cur.fetchmany(reference_count + 1)
            actual_length = len(rows) if rows else 0
            if not op(actual_length, reference_count):
                # fetching one b y one to keep the memory usage low
                while(True):
                    if not cur.fetchone():
                        # if no more elements, break the loop and raise the assertion error
                        break
                    # count how many there are
                    actual_length += 1
                raise AssertionError(f"Expected query to return {semantics[op]} {reference_count} rows, but got {actual_length}.")
        finally:
            if cur:
                self._dbconnection.rollback()


    @keyword(name="Query")
    def query(self, select_statement: str) -> List[Dict]:
        """Execute a select statement and return the results as a list of dictionaries

        Args:
            select_statement (str): SQL Select statement

        Returns:
            List[Dict]: List of dictionaries (table rows)
        """        
        cur = None
        try:
            limit = os.environ.get('QUERY_LIMIT', None)
            cur = self._dbconnection.cursor()
            logger.info('Executing : Query  |  %s ' % select_statement)
            if limit:
                logger.debug(f"Query will be limited to {limit} records.")
                limit = int(limit)
            self.execute_sql(cur, select_statement)
            allRows = cur.fetchmany(limit) if limit else cur.fetchall()
            mappedRows = []
            col_names = [c[0] for c in cur.description]

            for rowIdx in range(len(allRows)):
                d = {}
                for colIdx in range(len(allRows[rowIdx])):
                    d[col_names[colIdx]] = allRows[rowIdx][colIdx]
                mappedRows.append(d)
            cl.log_list(mappedRows)
            return mappedRows

        finally:
            if cur:
                self._dbconnection.rollback()

    @keyword(name="Description")
    def description(self, select_statement: str) -> List[str]:
        """Perform a query and return its cursor's description

        Args:
            select_statement (str): SQL Statement

        Returns:
            List[str]: list of strings describing the query results
        """        
        cur = None
        try:
            cur = self._dbconnection.cursor()
            logger.info(f'Executing: Description of {select_statement}')
            self.execute_sql(cur, select_statement)
            description = list(cur.description)
            return description
        finally:
            if cur:
                self._dbconnection.rollback()

    @keyword(name="Execute SQL Script")
    def execute_sql(self, cur, sqlStatement):
        return cur.execute(sqlStatement)
