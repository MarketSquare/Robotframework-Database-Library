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
from typing import Union

from robot.api import logger
from robot.api.deco import keyword, not_keyword
from robot.libraries.Collections import Collections

semantics = {
    le: ('at most'),
    ge: ('at least'),
    eq: ('exactly'),
    lt: ('less than'),
    gt: ('more than')
}

cl = Collections()


class Query:
    """
    Query handles all the querying done by the Database Library.
    """

    @not_keyword
    def asserted_query(self, selectStatement: str, expected_count: int, op: Union[le, ge, eq, lt, gt]) -> None:
        cur = None
        try:
            cur = self._dbconnection.cursor()
            logger.info(f'Executing: Query | {selectStatement}')
            logger.debug(f"Query will be limited to {expected_count + 1} records.")
            self.__execute_sql(cur, selectStatement)
            rows = cur.fetchmany(expected_count + 1)
            act_length = len(rows) if rows else 0
            if not op(act_length, expected_count):
                while(True):
                    if not cur.fetchone():
                        break
                    act_length += 1
                raise AssertionError(f"Expected query to return {semantics[op]} {expected_count} rows, but got {act_length}.")
        finally:
            if cur:
                self._dbconnection.rollback()


    @keyword(name="Query")
    def query(self, selectStatement: str):
        cur = None
        try:
            limit = os.environ.get('QUERY_LIMIT', None)
            cur = self._dbconnection.cursor()
            logger.info('Executing : Query  |  %s ' % selectStatement)
            if limit:
                logger.debug(f"Query will be limited to {limit} records.")
                limit = int(limit)
            self.__execute_sql(cur, selectStatement)
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
    def description(self, selectStatement):
        cur = None
        try:
            cur = self._dbconnection.cursor()
            logger.info('Executing : Description  |  %s ' % selectStatement)
            self.__execute_sql(cur, selectStatement)
            description = list(cur.description)
            return description
        finally:
            if cur:
                self._dbconnection.rollback()

    @not_keyword
    def __execute_sql(self, cur, sqlStatement):
        return cur.execute(sqlStatement)
