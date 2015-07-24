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

from robot.api import logger

class Query(object):
    """
    Query handles all the querying done by the Database Library.
    """

    def query(self, selectStatement, **named_args):
        """
        Uses the input `selectStatement` to query for the values that
        will be returned as a list of tuples.

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
        | Log Many | @{queryResults} |

        You will get the following:
        [1, 'Franz Allan', 'See']

        Also, you can do something like this:
        | ${queryResults} | Query | SELECT first_name, last_name FROM person |
        | Log | ${queryResults[0][1]}, ${queryResults[0][0]} |

        And get the following
        See, Franz Allan
        """
        with self._dbconnection.begin():
            return self._dbconnection.execute(selectStatement, **named_args).fetchall()

    def row_count(self, selectStatement, **named_args):
        """
        Uses the input `selectStatement` to query the database and returns
        the number of rows from the query.

        For example, given we have a table `person` with the following data:
        | id | first_name  | last_name |
        |  1 | Franz Allan | See       |
        |  2 | Jerry       | Schneider |

        When you do the following:
        | ${rowCount} | Row Count | SELECT * FROM person |
        | Log | ${rowCount} |

        You will get the following:
        2

        Also, you can do something like this:
        | ${rowCount} | Row Count | SELECT * FROM person WHERE id = 2 |
        | Log | ${rowCount} |

        And get the following
        1
        """
        return len(self.query(selectStatement, **named_args))

    def description(self, selectStatement, **named_args):
        """
        Uses the input `selectStatement` to query a table in the db which
        will be used to determine the description.

        For example, given we have a table `person` with the following data:
        | id | first_name  | last_name |
        |  1 | Franz Allan | See       |

        When you do the following:
        | @{queryResults} | Description | SELECT * FROM person |
        | Log Many | @{queryResults} |

        You will get the following:
        [Column(name='id', type_code=1043, display_size=None, internal_size=255, precision=None, scale=None, null_ok=None)]
        [Column(name='first_name', type_code=1043, display_size=None, internal_size=255, precision=None, scale=None, null_ok=None)]
        [Column(name='last_name', type_code=1043, display_size=None, internal_size=255, precision=None, scale=None, null_ok=None)]
        """
        with self._dbconnection.begin():
            return self._dbconnection.execute(selectStatement, **named_args)._cursor_description()

    def delete_all_rows_from_table(self, tableName):
        """
        Delete all the rows within a given table.

        For example, given we have a table `person` in a database

        When you do the following:
        | Delete All Rows From Table | person |

        If all the rows can be successfully deleted, then you will get:
        | Delete All Rows From Table | person | # PASS |
        If the table doesn't exist or all the data can't be deleted, then you
        will get:
        | Delete All Rows From Table | first_name | # FAIL |
        """
        cur = None
        selectStatement = ("DELETE FROM %s;" % tableName)
        try:
            cur = self._dbconnection.cursor()
            result = self.__execute_sql(cur, selectStatement)
            if result is not None:
                self._dbconnection.commit()
                return result
            self._dbconnection.commit()
        finally :
            if cur :
                self._dbconnection.rollback()

    def is_comment(self, sql_line):
        sql_line = sql_line.strip()
        return sql_line.startswith('--') or sql_line.startswith('#')

    def _remove_comments(self, sql):
        lines = [line for line in sql.split('\n') if not self.is_comment(line)]
        lines = [line.strip() for line in lines if not len(line.strip()) == 0]
        return '\n'.join(lines)

    def _split_sql_script(self, sql):
        """
        Splits an SQL script into semicolon (';')-separated queries,
        ignoring any line that starts wih '--' or '#'.

        >>> Query()._split_sql_script('select name;')
        ['select name']
        >>> Query()._split_sql_script('''select name;
        ... select lname;''')
        ['select name', 'select lname']
        >>> Query()._split_sql_script('''select name;
        ... -- This is a comment
        ... # This is also a comment
        ... select lname;''')
        ['select name', 'select lname']
        """
        lines = list()
        queries = sql.split(';')
        queries = [self._remove_comments(q) for q in queries if len(q.strip()) > 0]
        return queries

    def execute_sql_script(self, sqlScriptFileName, **named_args):
        """
        Executes the content of the `sqlScriptFileName` as SQL commands.
        Useful for setting the database to a known state before running
        your tests, or clearing out your test data after running each a
        test.

        Sample usage :
        | Execute Sql Script | ${EXECDIR}${/}resources${/}DDL-setup.sql |
        | Execute Sql Script | ${EXECDIR}${/}resources${/}DML-setup.sql |
        | #interesting stuff here |
        | Execute Sql Script | ${EXECDIR}${/}resources${/}DML-teardown.sql |
        | Execute Sql Script | ${EXECDIR}${/}resources${/}DDL-teardown.sql |

        SQL commands are expected to be delimited by a semi-colon (';').

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

        However, lines that starts with a number sign (`#`) are treated as a
        commented line. Thus, none of the contents of that line will be executed.

        For example:
        # Delete the bridging table first...
        DELETE
          FROM person_employee_table;
          # ...and then the bridged tables.
        DELETE
          FROM person_table;
        DELETE
          FROM employee_table
        """
        with open(sqlScriptFileName) as sqlScriptFile:
            queries = self._split_sql_script(sqlScriptFile.read())
            self._run_query_list(queries, **named_args)

    def execute_sql_string(self, sqlString, **named_args):
        """
        Executes the sqlString as SQL commands.
        Useful to pass arguments to your sql.

        SQL commands are expected to be delimited by a semi-colon (';').

        For example:
        | Execute Sql String | DELETE FROM person_employee_table; DELETE FROM person_table |

        For example with an argument:
        | Execute Sql String | SELECT * FROM person WHERE first_name = ${FIRSTNAME} |

        You can also use :bind variables in your query:
        | Execute Sql String | SELECT * FROM person WHERE first_name = :fname | fname=${FIRSTNAME} |

        NOTE: This keyword makes no effort to distinguish between semi-colons
        inside String literals and those separating queries.

        This will break (use the 'Query' keyword instead):
        | Execute Sql String | SELECT * FROM person WHERE full_name_semicolon = 'john;doe' |
        """
        self._run_query_list(sqlString.split(';'), **named_args)

    def _run_query_list(self, queries, **named_args):
        with self._dbconnection.begin():
            for query in queries:
                self._dbconnection.execute(query, **named_args)

    def __execute_sql(self, cur, sqlStatement):
        logger.debug("Executing : %s" % sqlStatement)
        return cur.execute(sqlStatement)
