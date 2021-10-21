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
from typing import Optional

from robot.api import logger


class Assertion:
    """
    Assertion handles all the assertions of Database Library.
    """

    def check_if_exists_in_database(self, selectStatement: str, sansTran: bool = False, msg: Optional[str] = None, alias: Optional[str] = None):
        """
        Check if any row would be returned by given the input `selectStatement`. If there are no results, then this will
        throw an AssertionError. Set optional input `sansTran` to True to run command without an explicit transaction
        commit or rollback. The default error message can be overridden with the `msg` argument.

        For example, given we have a table `person` with the following data:
        | id | first_name  | last_name |
        |  1 | Franz Allan | See       |

        When you have the following assertions in your robot
        | Check If Exists In Database | SELECT id FROM person WHERE first_name = 'Franz Allan' |
        | Check If Exists In Database | SELECT id FROM person WHERE first_name = 'John' |
        | Check If Exists In Database | SELECT id FROM person WHERE first_name = 'Franz Allan' | alias=my_alias |

        Then you will get the following:
        | Check If Exists In Database | SELECT id FROM person WHERE first_name = 'Franz Allan' | # PASS |
        | Check If Exists In Database | SELECT id FROM person WHERE first_name = 'John' | # FAIL |

        Using optional `sansTran` to run command without an explicit transaction commit or rollback:
        | Check If Exists In Database | SELECT id FROM person WHERE first_name = 'John' | True |

        Using optional `msg` to override the default error message:
        | Check If Exists In Database | SELECT id FROM person WHERE first_name = 'John' | msg=my error message |
        """
        logger.info(f"Executing : Check If Exists In Database  |  {selectStatement}")
        if not self.query(selectStatement, sansTran, alias=alias):
            raise AssertionError(
                msg or f"Expected to have have at least one row, but got 0 rows from: '{selectStatement}'"
            )

    def check_if_not_exists_in_database(self, selectStatement: str, sansTran: bool = False, msg: Optional[str] = None, alias: Optional[str] = None):
        """
        This is the negation of `check_if_exists_in_database`.

        Check if no rows would be returned by given the input `selectStatement`. If there are any results, then this
        will throw an AssertionError. Set optional input `sansTran` to True to run command without an explicit
        transaction commit or rollback. The default error message can be overridden with the `msg` argument.

        For example, given we have a table `person` with the following data:
        | id | first_name  | last_name |
        |  1 | Franz Allan | See       |

        When you have the following assertions in your robot
        | Check If Not Exists In Database | SELECT id FROM person WHERE first_name = 'John' |
        | Check If Not Exists In Database | SELECT id FROM person WHERE first_name = 'Franz Allan' |
        | Check If Not Exists In Database | SELECT id FROM person WHERE first_name = 'Franz Allan' | alias=my_alias |

        Then you will get the following:
        | Check If Not Exists In Database | SELECT id FROM person WHERE first_name = 'John' | # PASS |
        | Check If Not Exists In Database | SELECT id FROM person WHERE first_name = 'Franz Allan' | # FAIL |

        Using optional `sansTran` to run command without an explicit transaction commit or rollback:
        | Check If Not Exists In Database | SELECT id FROM person WHERE first_name = 'John' | True |

        Using optional `msg` to override the default error message:
        | Check If Not Exists In Database | SELECT id FROM person WHERE first_name = 'Franz Allan' | msg=my error message |
        """
        logger.info(f"Executing : Check If Not Exists In Database  |  {selectStatement}")
        query_results = self.query(selectStatement, sansTran, alias=alias)
        if query_results:
            raise AssertionError(
                msg or f"Expected to have have no rows from '{selectStatement}', but got some rows: {query_results}"
            )

    def row_count_is_0(self, selectStatement: str, sansTran: bool = False, msg: Optional[str] = None, alias: Optional[str] = None):
        """
        Check if any rows are returned from the submitted `selectStatement`. If there are, then this will throw an
        AssertionError. Set optional input `sansTran` to True to run command without an explicit transaction commit or
        rollback. The default error message can be overridden with the `msg` argument.

        For example, given we have a table `person` with the following data:
        | id | first_name  | last_name |
        |  1 | Franz Allan | See       |

        When you have the following assertions in your robot
        | Row Count is 0 | SELECT id FROM person WHERE first_name = 'Franz Allan' |
        | Row Count is 0 | SELECT id FROM person WHERE first_name = 'John' |
        | Row Count is 0 | SELECT id FROM person WHERE first_name = 'John' | alias=my_alias |

        Then you will get the following:
        | Row Count is 0 | SELECT id FROM person WHERE first_name = 'Franz Allan' | # FAIL |
        | Row Count is 0 | SELECT id FROM person WHERE first_name = 'John' | # PASS |

        Using optional `sansTran` to run command without an explicit transaction commit or rollback:
        | Row Count is 0 | SELECT id FROM person WHERE first_name = 'John' | True |

        Using optional `msg` to override the default error message:
        | Row Count is 0 | SELECT id FROM person WHERE first_name = 'Franz Allan' | msg=my error message |
        """
        logger.info(f"Executing : Row Count Is 0  |  {selectStatement}")
        num_rows = self.row_count(selectStatement, sansTran, alias=alias)
        if num_rows > 0:
            raise AssertionError(msg or f"Expected 0 rows, but {num_rows} were returned from: '{selectStatement}'")

    def row_count_is_equal_to_x(
        self, selectStatement: str, numRows: str, sansTran: bool = False, msg: Optional[str] = None, alias: Optional[str] = None
    ):
        """
        Check if the number of rows returned from `selectStatement` is equal to the value submitted. If not, then this
        will throw an AssertionError. Set optional input `sansTran` to True to run command without an explicit
        transaction commit or rollback. The default error message can be overridden with the `msg` argument.

        For example, given we have a table `person` with the following data:
        | id | first_name  | last_name |
        |  1 | Franz Allan | See       |
        |  2 | Jerry       | Schneider |

        When you have the following assertions in your robot
        | Row Count Is Equal To X | SELECT id FROM person | 1 |
        | Row Count Is Equal To X | SELECT id FROM person WHERE first_name = 'John' | 0 |
        | Row Count Is Equal To X | SELECT id FROM person WHERE first_name = 'John' | 0 | alias=my_alias |

        Then you will get the following:
        | Row Count Is Equal To X | SELECT id FROM person | 1 | # FAIL |
        | Row Count Is Equal To X | SELECT id FROM person WHERE first_name = 'John' | 0 | # PASS |

        Using optional `sansTran` to run command without an explicit transaction commit or rollback:
        | Row Count Is Equal To X | SELECT id FROM person WHERE first_name = 'John' | 0 | True |

        Using optional `msg` to override the default error message:
        | Row Count Is Equal To X | SELECT id FROM person | 1 | msg=my error message |
        """
        logger.info(f"Executing : Row Count Is Equal To X  |  {selectStatement}  |  {numRows}")
        num_rows = self.row_count(selectStatement, sansTran, alias=alias)
        if num_rows != int(numRows.encode("ascii")):
            raise AssertionError(
                msg or f"Expected {numRows} rows, but {num_rows} were returned from: '{selectStatement}'"
            )

    def row_count_is_greater_than_x(
        self, selectStatement: str, numRows: str, sansTran: bool = False, msg: Optional[str] = None, alias: Optional[str] = None
    ):
        """
        Check if the number of rows returned from `selectStatement` is greater than the value submitted. If not, then
        this will throw an AssertionError. Set optional input `sansTran` to True to run command without an explicit
        transaction commit or rollback. The default error message can be overridden with the `msg` argument.

        For example, given we have a table `person` with the following data:
        | id | first_name  | last_name |
        |  1 | Franz Allan | See       |
        |  2 | Jerry       | Schneider |

        When you have the following assertions in your robot
        | Row Count Is Greater Than X | SELECT id FROM person | 1 |
        | Row Count Is Greater Than X | SELECT id FROM person WHERE first_name = 'John' | 0 |
        | Row Count Is Greater Than X | SELECT id FROM person WHERE first_name = 'John' | 0 | alias=my_alias |

        Then you will get the following:
        | Row Count Is Greater Than X | SELECT id FROM person | 1 | # PASS |
        | Row Count Is Greater Than X | SELECT id FROM person WHERE first_name = 'John' | 0 | # FAIL |

        Using optional `sansTran` to run command without an explicit transaction commit or rollback:
        | Row Count Is Greater Than X | SELECT id FROM person | 1 | True |

        Using optional `msg` to override the default error message:
        | Row Count Is Greater Than X | SELECT id FROM person WHERE first_name = 'John' | 0 | msg=my error message |
        """
        logger.info(f"Executing : Row Count Is Greater Than X  |  {selectStatement}  |  {numRows}")
        num_rows = self.row_count(selectStatement, sansTran, alias=alias)
        if num_rows <= int(numRows.encode("ascii")):
            raise AssertionError(
                msg or f"Expected more than {numRows} rows, but {num_rows} were returned from '{selectStatement}'"
            )

    def row_count_is_less_than_x(
        self, selectStatement: str, numRows: str, sansTran: bool = False, msg: Optional[str] = None, alias: Optional[str] = None
    ):
        """
        Check if the number of rows returned from `selectStatement` is less than the value submitted. If not, then this
        will throw an AssertionError. Set optional input `sansTran` to True to run command without an explicit
        transaction commit or rollback.

        For example, given we have a table `person` with the following data:
        | id | first_name  | last_name |
        |  1 | Franz Allan | See       |
        |  2 | Jerry       | Schneider |

        When you have the following assertions in your robot
        | Row Count Is Less Than X | SELECT id FROM person | 3 |
        | Row Count Is Less Than X | SELECT id FROM person WHERE first_name = 'John' | 1 |
        | Row Count Is Less Than X | SELECT id FROM person WHERE first_name = 'John' | 1 | alias=my_alias |

        Then you will get the following:
        | Row Count Is Less Than X | SELECT id FROM person | 3 | # PASS |
        | Row Count Is Less Than X | SELECT id FROM person WHERE first_name = 'John' | 1 | # FAIL |

        Using optional `sansTran` to run command without an explicit transaction commit or rollback:
        | Row Count Is Less Than X | SELECT id FROM person | 3 | True |

        Using optional `msg` to override the default error message:
        | Row Count Is Less Than X | SELECT id FROM person WHERE first_name = 'John' | 1 | msg=my error message |
        """
        logger.info(f"Executing : Row Count Is Less Than X  |  {selectStatement}  |  {numRows}")
        num_rows = self.row_count(selectStatement, sansTran, alias=alias)
        if num_rows >= int(numRows.encode("ascii")):
            raise AssertionError(
                msg or f"Expected less than {numRows} rows, but {num_rows} were returned from '{selectStatement}'"
            )

    def table_must_exist(self, tableName: str, sansTran: bool = False, msg: Optional[str] = None, alias: Optional[str] = None):
        """
        Check if the table given exists in the database. Set optional input `sansTran` to True to run command without an
        explicit transaction commit or rollback. The default error message can be overridden with the `msg` argument.

        For example, given we have a table `person` in a database

        When you do the following:
        | Table Must Exist | person |

        Then you will get the following:
        | Table Must Exist | person | # PASS |
        | Table Must Exist | first_name | # FAIL |
        | Table Must Exist | first_name | alias=my_alias |

        Using optional `sansTran` to run command without an explicit transaction commit or rollback:
        | Table Must Exist | person | True |

        Using optional `msg` to override the default error message:
        | Table Must Exist | first_name | msg=my error message |
        """
        logger.info(f"Executing : Table Must Exist  |  {tableName}")
        _, db_api_module_name = self._cache.switch(alias)
        if db_api_module_name in ["cx_Oracle", "oracledb"]:
            query = (
                "SELECT * FROM all_objects WHERE object_type IN ('TABLE','VIEW') AND "
                f"owner = SYS_CONTEXT('USERENV', 'SESSION_USER') AND object_name = UPPER('{tableName}')"
            )
            table_exists = self.row_count(query, sansTran, alias=alias) > 0
        elif db_api_module_name in ["sqlite3"]:
            query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tableName}' COLLATE NOCASE"
            table_exists = self.row_count(query, sansTran, alias=alias) > 0
        elif db_api_module_name in ["ibm_db", "ibm_db_dbi"]:
            query = f"SELECT name FROM SYSIBM.SYSTABLES WHERE type='T' AND name=UPPER('{tableName}')"
            table_exists = self.row_count(query, sansTran, alias=alias) > 0
        elif db_api_module_name in ["teradata"]:
            query = f"SELECT TableName FROM DBC.TablesV WHERE TableKind='T' AND TableName='{tableName}'"
            table_exists = self.row_count(query, sansTran, alias=alias) > 0
        else:
            try:
                query = f"SELECT * FROM information_schema.tables WHERE table_name='{tableName}'"
                table_exists = self.row_count(query, sansTran, alias=alias) > 0
            except:
                logger.info("Database doesn't support information schema, try using a simple SQL request")
                try:
                    query = f"SELECT 1 from {tableName} where 1=0"
                    self.row_count(query, sansTran, alias=alias)
                    table_exists = True
                except:
                    table_exists = False
        assert table_exists, msg or f"Table '{tableName}' does not exist in the db"
