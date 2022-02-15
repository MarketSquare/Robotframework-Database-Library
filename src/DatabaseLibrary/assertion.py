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

from operator import eq, ge, gt, le, lt

from robot.api import logger
from robot.api.deco import keyword, not_keyword


class Assertion:
    """
    Assertion handles all the assertions of Database Library.
    """

    @keyword(name="Check If Exists In Database")
    def check_if_exists_in_database(self, selectStatement):
        logger.info (f'Asserting: Check If Exists In Database')
        self.asserted_query(selectStatement, 0, gt)

    @keyword(name="Check If Not Exists In Database")
    def check_if_not_exists_in_database(self, selectStatement):
        logger.info(f'Asserting: Check If Not Exists In Database')
        self.asserted_query(selectStatement, 0, lt)

    @keyword(name="Row Count Is 0")
    def row_count_is_0(self, selectStatement):
        logger.info(f'Asserting: Row Count Is 0')
        self.asserted_query(selectStatement, 0, eq)

    @keyword(name="Row Count Is Equal To X")
    def row_count_is_equal_to_x(self, selectStatement, numRows):
        logger.info(f'Asserting: Row Count Is Equal To {numRows}')
        self.asserted_query(selectStatement, numRows, eq)

    def row_count_is_greater_than_x(self, selectStatement, numRows):
        logger.info(f'Asserting: Row Count Is Greater Than {numRows}')
        self.asserted_query(selectStatement, numRows, gt)

    def row_count_is_less_than_x(self, selectStatement, numRows):
        logger.info(f'Asserting: Row Count Is Less Than {numRows}')
        self.asserted_query(selectStatement, numRows, lt)

    def row_count_is_at_least_x(self, selectStatement, numRows):
        logger.info(f'Asserting: Row Count Is At Least {numRows}')
        self.asserted_query(selectStatement, numRows, ge)

    def row_count_is_at_most_x(self, selectStatement, numRows):
        logger.info(f'Asserting: Row Count Is At Most {numRows}')
        self.asserted_query(selectStatement, numRows, le)

    def table_must_exist(self, tableName):
        logger.info(f'Asserting: Table {tableName} Must Exist')
        if self.db_api_module_name in ["cx_Oracle"]:
            selectStatement = f"SELECT * FROM all_objects WHERE object_type IN ('TABLE','VIEW') AND owner = SYS_CONTEXT('USERENV', 'SESSION_USER') AND object_name = UPPER('{tableName}')"
        elif self.db_api_module_name in ["sqlite3"]:
            selectStatement = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tableName}' COLLATE NOCASE"
        elif self.db_api_module_name in ["ibm_db", "ibm_db_dbi"]:
            selectStatement = f"SELECT name FROM SYSIBM.SYSTABLES WHERE type='T' AND name=UPPER('{tableName}')"
        elif self.db_api_module_name in ["teradata"]:
            selectStatement = f"SELECT TableName FROM DBC.TablesV WHERE TableKind='T' AND TableName='{tableName}'"
        else:
            selectStatement = f"SELECT * FROM information_schema.tables WHERE table_name='{tableName}'"
        num_rows = self.row_count(selectStatement)
        if num_rows == 0:
            raise AssertionError(f"Table '{tableName}' does not exist in the db")
