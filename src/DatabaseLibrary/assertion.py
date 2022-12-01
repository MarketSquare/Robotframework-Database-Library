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

from exceptions import TechnicalTestFailure
from func_timeout import FunctionTimedOut
from robot.api import logger
from robot.api.deco import keyword


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
        try:
            self.asserted_query(select_statement, 0, gt)
        except FunctionTimedOut:
            raise AssertionError(f"Query timed out.")
        except TechnicalTestFailure as ttf:
            raise TechnicalTestFailure(
                f"Could not check whether result has rows because of error: {str(ttf)}") from ttf
        except Exception as ex:
            raise TechnicalTestFailure(
                f"Could not check whether result has rows because of error: {str(ex)}")

    @keyword(name="Check If Not Exists In Database")
    def check_if_not_exists_in_database(self, select_statement: str) -> None:
        """Checks if the SQL Statement returned any rows, expects at most 0.

        Args:
            select_statement (str): SQL Select Statement
        """
        logger.info(f"Asserting: Check If Not Exists In Database")
        try:
            self.asserted_query(select_statement, 0, lt)
        except FunctionTimedOut:
            raise AssertionError(f"Query timed out.")
        except TechnicalTestFailure as ttf:
            raise TechnicalTestFailure(
                f"Could not check whether result has no rows because of error: {str(ttf)}") from ttf
        except Exception as ex:
            raise TechnicalTestFailure(
                f"Could not check whether result has no rows because of error: {str(ex)}")

    @keyword(name="Row Count Is 0")
    def row_count_is_0(self, select_statement: str) -> None:
        """Checks whether SQL Statement returns exactly 0 rows.

        Args:
            select_statement (str): SQL Select Statement
        """
        logger.info(f"Asserting: Row Count Is 0")
        try:
            self.asserted_query(select_statement, 0, eq)
        except FunctionTimedOut:
            raise AssertionError(f"Query timed out.")
        except TechnicalTestFailure as ttf:
            raise TechnicalTestFailure(
                f"Could not check whether row count is 0 because of error: {str(ttf)}") from ttf
        except Exception as ex:
            raise TechnicalTestFailure(
                f"Could not check whether row count is 0 because of error: {str(ex)}")

    @keyword(name="Row Count Is Equal To X")
    def row_count_is_equal_to_x(
        self, select_statement: str, row_reference_count: int
    ) -> None:
        """Checks whether SQL Statement returns exactly X rows.

        Args:
            select_statement (str): SQL Select Statement
            row_reference_count (int): reference count for the comparison
        """
        logger.info(f"Asserting: Row Count Is Equal To {row_reference_count}")
        try:
            self.asserted_query(select_statement, row_reference_count, eq)
        except FunctionTimedOut:
            raise AssertionError(f"Query timed out.")
        except TechnicalTestFailure as ttf:
            raise TechnicalTestFailure(
                f"Could not check whether row count is exactly {row_reference_count} because of error: {str(ttf)}") from ttf
        except Exception as ex:
            raise TechnicalTestFailure(
                f"Could not check whether row count is exactly {row_reference_count} because of error: {str(ex)}")

    @keyword(name="Row Count Is Greater Than X")
    def row_count_is_greater_than_x(
        self, select_statement: str, row_reference_count: int
    ) -> None:
        """Checks whether SQL Statement returns more than X rows.

        Args:
            select_statement (str): SQL Select Statement
            row_reference_count (int): reference count for the comparison
        """
        logger.info(
            f"Asserting: Row Count Is Greater Than {row_reference_count}")
        try:
            self.asserted_query(select_statement, row_reference_count, gt)
        except FunctionTimedOut:
            raise AssertionError(f"Query timed out.")
        except TechnicalTestFailure as ttf:
            raise TechnicalTestFailure(
                f"Could not check whether row count is greater than {row_reference_count} because of error: {str(ttf)}") from ttf
        except Exception as ex:
            raise TechnicalTestFailure(
                f"Could not check whether row count is greater than {row_reference_count} because of error: {str(ex)}")

    @keyword("Row Count Is Less Than X")
    def row_count_is_less_than_x(
        self, select_statement: str, row_reference_count: int
    ) -> None:
        """Checks whether SQL Statement returns less than X rows.

        Args:
            select_statement (str): SQL Select Statement
            row_reference_count (int): reference count for the comparison
        """
        logger.info(f"Asserting: Row Count Is Less Than {row_reference_count}")
        try:
            self.asserted_query(select_statement, row_reference_count, lt)
        except FunctionTimedOut:
            raise AssertionError(f"Query timed out.")
        except TechnicalTestFailure as ttf:
            raise TechnicalTestFailure(
                f"Could not check whether row count is less than {row_reference_count} because of error: {str(ttf)}") from ttf
        except Exception as ex:
            raise TechnicalTestFailure(
                f"Could not check whether row count is less than {row_reference_count} because of error: {str(ex)}")

    @keyword("Row Count Is At Least X")
    def row_count_is_at_least_x(
        self, select_statement: str, row_reference_count: int
    ) -> None:
        """Checks whether SQL Statement returns X or more rows.

        Args:
            select_statement (str): SQL Select Statement
            row_reference_count (int): reference count for the comparison
        """
        logger.info(f"Asserting: Row Count Is At Least {row_reference_count}")
        try:
            self.asserted_query(select_statement, row_reference_count, ge)
        except FunctionTimedOut:
            raise AssertionError(f"Query timed out.")
        except TechnicalTestFailure as ttf:
            raise TechnicalTestFailure(
                f"Could not check whether row count is at least {row_reference_count} because of error: {str(ttf)}") from ttf
        except Exception as ex:
            raise TechnicalTestFailure(
                f"Could not check whether row count is at least {row_reference_count} because of error: {str(ex)}")

    @keyword("Row Count Is At Most X")
    def row_count_is_at_most_x(
        self, select_statement: str, row_reference_count: int
    ) -> None:
        """Checks whether SQL Statement no more than X rows.

        Args:
            select_statement (str): SQL Select Statement
            row_reference_count (int): reference count for the comparison
        """
        logger.info(f"Asserting: Row Count Is At Most {row_reference_count}")
        try:
            self.asserted_query(select_statement, row_reference_count, le)
        except FunctionTimedOut:
            raise AssertionError(f"Query timed out.")
        except TechnicalTestFailure as ttf:
            raise TechnicalTestFailure(
                f"Could not check whether row count is at most {row_reference_count} because of error: {str(ttf)}") from ttf
        except Exception as ex:
            raise TechnicalTestFailure(
                f"Could not check whether row count is at most {row_reference_count} because of error: {str(ex)}")

    @keyword(name="Table Must Exist")
    def table_must_exist(self, table_name: str):
        """Checks whether a given table exists

        Args:
            table_name (str): name of the table in the database

        Raises:
            AssertionError: when table does not exist
        """
        logger.info(f"Asserting: Table {table_name} Must Exist")
        if self.db_api_module_name in ["cx_Oracle"]:
            select_statement = f"SELECT * FROM all_objects WHERE object_type IN ('TABLE','VIEW') AND owner = SYS_CONTEXT('USERENV', 'SESSION_USER') AND object_name = UPPER('{table_name}')"
        elif self.db_api_module_name in ["sqlite3"]:
            select_statement = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}' COLLATE NOCASE"
        elif self.db_api_module_name in ["ibm_db", "ibm_db_dbi"]:
            select_statement = f"SELECT name FROM SYSIBM.SYSTABLES WHERE type='T' AND name=UPPER('{table_name}')"
        elif self.db_api_module_name in ["teradata"]:
            select_statement = f"SELECT table_name FROM DBC.TablesV WHERE TableKind='T' AND table_name='{table_name}'"
        else:
            select_statement = f"SELECT * FROM information_schema.tables WHERE table_name='{table_name}'"
        try:
            self.asserted_query(select_statement, 0, gt)
        except AssertionError:
            raise AssertionError(f"Table {table_name} does not exist.")
        except FunctionTimedOut:
            raise AssertionError(f"Query timed out.")
        except TechnicalTestFailure as ttf:
            raise TechnicalTestFailure(
                f"Could not check whether table exists due to error: {str(ttf)}") from ttf
        except Exception as ex:
            raise TechnicalTestFailure(
                f"Could not check whether table exists due to error: {str(ex)}")
