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
from typing import Dict, List, Union

from func_timeout import FunctionTimedOut
from robot.api import logger
from robot.api.deco import keyword, not_keyword

from .exceptions import TechnicalTestFailure, TestFailure


class Assertion:
    """
    Assertion handles all the assertions of Database Library.
    """

    @keyword(name="Check If Exists In Database")
    def check_if_exists_in_database(self, select_statement: str) -> None:
        """Checks if the SQL Statement returned any rows, expects at least 1.

        Args:
            select_statement (str): SQL Select Statement
        """
        logger.info(f"Asserting: Check If Exists In Database")
        self.row_count_is_greater_than_x(select_statement, 0)

    @keyword(name="Check If Not Exists In Database")
    def check_if_not_exists_in_database(self, select_statement: str) -> None:
        """Checks if the SQL Statement returned any rows, expects at most 0.

        Args:
            select_statement (str): SQL Select Statement
        """
        logger.info(f"Asserting: Check If Not Exists In Database")
        self.row_count_is_0(select_statement)

    @keyword(name="Row Count Is 0")
    def row_count_is_0(self, select_statement: str) -> None:
        """Checks whether SQL Statement returns exactly 0 rows.

        Args:
            select_statement (str): SQL Select Statement
        """
        self.row_count_is_equal_to_x(select_statement, 0)

    @keyword(name="Row Count Is Equal To X")
    def row_count_is_equal_to_x(
        self, select_statement: str, row_reference_count: int
    ) -> None:
        """Checks whether SQL Statement returns exactly X rows.

        Args:
            select_statement (str): SQL Select Statement
            row_reference_count (int): reference count for the comparison
        """
        message = f"Row Count Is Equal To {row_reference_count}"
        logger.info(f"Asserting: {message}")
        self._asserted_query_wrapper(
            select_statement, row_reference_count, eq, message)

    @keyword(name="Row Count Is Greater Than X")
    def row_count_is_greater_than_x(
        self, select_statement: str, row_reference_count: int
    ) -> None:
        """Checks whether SQL Statement returns more than X rows.

        Args:
            select_statement (str): SQL Select Statement
            row_reference_count (int): reference count for the comparison
        """
        message = f"Row Count Is Greater Than {row_reference_count}"
        logger.info(f"Asserting: {message}")
        self._asserted_query_wrapper(
            select_statement, row_reference_count, gt, message)

    @keyword("Row Count Is Less Than X")
    def row_count_is_less_than_x(
        self, select_statement: str, row_reference_count: int
    ) -> None:
        """Checks whether SQL Statement returns less than X rows.

        Args:
            select_statement (str): SQL Select Statement
            row_reference_count (int): reference count for the comparison
        """
        message = "Row Count Is Less Than {row_reference_count}"
        logger.info(f"Asserting: {message}")
        self._asserted_query_wrapper(
            select_statement, row_reference_count, lt, message)

    @keyword("Row Count Is At Least X")
    def row_count_is_at_least_x(
        self, select_statement: str, row_reference_count: int
    ) -> None:
        """Checks whether SQL Statement returns X or more rows.

        Args:
            select_statement (str): SQL Select Statement
            row_reference_count (int): reference count for the comparison
        """
        message = f"Row Count Is At Least {row_reference_count}"
        logger.info(f"Asserting: {message}")
        self._asserted_query_wrapper(
            select_statement, row_reference_count, ge, message)

    @keyword("Row Count Is At Most X")
    def row_count_is_at_most_x(
        self, select_statement: str, row_reference_count: int
    ) -> None:
        """Checks whether SQL Statement no more than X rows.

        Args:
            select_statement (str): SQL Select Statement
            row_reference_count (int): reference count for the comparison
        """
        message = f"Row Count Is At Most {row_reference_count}"
        logger.info(f"Asserting: {message}")
        self._asserted_query_wrapper(
            select_statement, row_reference_count, le, message)

    @keyword(name="Table Must Exist")
    def table_must_exist(self, table_name: str):
        """Checks whether a given table exists

        Args:
            table_name (str): name of the table in the database

        Raises:
            AssertionError: when table does not exist
        """
        message = f"Table {table_name} Must Exist"
        logger.info(f"Asserting: {message}")
        table_exists = {
            "cx_oracle": f"SELECT * FROM all_objects WHERE object_type IN ('TABLE','VIEW') AND owner = SYS_CONTEXT('USERENV', 'SESSION_USER') AND object_name = UPPER('{table_name}')",
            "sqlite3": f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}' COLLATE NOCASE",
            "ibm_db": f"SELECT name FROM SYSIBM.SYSTABLES WHERE type='T' AND name=UPPER('{table_name}')",
            "ibm_db_dbi": f"SELECT name FROM SYSIBM.SYSTABLES WHERE type='T' AND name=UPPER('{table_name}')",
            "teradata": f"SELECT table_name FROM DBC.TablesV WHERE TableKind='T' AND table_name='{table_name}'"
        }
        select_statement = table_exists.get(
            self.db_api_module_name, f"SELECT * FROM information_schema.tables WHERE table_name='{table_name}'")

        self._asserted_query_wrapper(
            select_statement, 0, gt, message)

    @not_keyword
    def _asserted_query_wrapper(self, select_statement: str, reference_count: int, op: Union[le, ge, eq, lt, gt], check_message: str):
        try:
            self.asserted_query(select_statement, reference_count, op)
        # Test FAIL result:
        except TestFailure as tf:
            raise AssertionError(
                f"{check_message} failed: {str(tf)}") from tf
        # test ERROR result:
        except FunctionTimedOut:
            raise
        except TechnicalTestFailure as ttf:
            raise TechnicalTestFailure(
                f"Cannot determine whether `{check_message}` because of error: \nDetails: {str(ttf)}") from ttf
        except Exception as ex:
            raise TechnicalTestFailure(
                f"Cannot determine whether `{check_message}` because of unexpected error: \nDetails: {str(ex)}") from ex
