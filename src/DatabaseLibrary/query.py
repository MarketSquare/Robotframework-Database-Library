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

    def query(self, selectStatement):
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
        | @{queryResults} | Query | select * from person |
        | Log Many | @{queryResults} |
        
        You will get the following:
        [1, 'Franz Allan', 'See']
        
        Also, you can do something like this:
        | ${queryResults} | Query | select first_name, last_name from person |
        | Log | ${queryResults[0][1]}, ${queryResults[0][0]} |
        
        And get the following
        See, Franz Allan
        """
        cur = None
        try:
            cur = self._dbconnection.cursor()
            self.__execute_sql(cur, selectStatement)
            allRows = cur.fetchall()
            return allRows
        finally :
            if cur :
                self._dbconnection.rollback() 

    def row_count(self, selectStatement):
        """
        Uses the input `selectStatement` to query the database and returns
        the number of rows from the query.
        
        For example, given we have a table `person` with the following data:
        | id | first_name  | last_name |
        |  1 | Franz Allan | See       |
        |  2 | Jerry       | Schneider |
        
        When you do the following:
        | ${rowCount} | Row Count | select * from person |
        | Log | ${rowCount} |
        
        You will get the following:
        2
        
        Also, you can do something like this:
        | ${rowCount} | Row Count | select * from person where id = 2 |
        | Log | ${rowCount} |
        
        And get the following
        1
        """
        cur = None
        try:
            cur = self._dbconnection.cursor()
            self.__execute_sql(cur, selectStatement)
            cur.fetchall()
            rowCount = cur.rowcount
            return rowCount
        finally :
            if cur :
                self._dbconnection.rollback() 

    def description(self, selectStatement):
        """
        Uses the input `selectStatement` to query a table in the db which
        will be used to determine the description.
                
        For example, given we have a table `person` with the following data:
        | id | first_name  | last_name |
        |  1 | Franz Allan | See       |
        
        When you do the following:
        | @{queryResults} | Description | select * from person |
        | Log Many | @{queryResults} |
        
        You will get the following:
        [Column(name='id', type_code=1043, display_size=None, internal_size=255, precision=None, scale=None, null_ok=None)]
        [Column(name='first_name', type_code=1043, display_size=None, internal_size=255, precision=None, scale=None, null_ok=None)]
        [Column(name='last_name', type_code=1043, display_size=None, internal_size=255, precision=None, scale=None, null_ok=None)]
        """
        cur = None
        try:
            cur = self._dbconnection.cursor()
            self.__execute_sql(cur, selectStatement)
            description = cur.description
            return description
        finally :
            if cur :
                self._dbconnection.rollback() 

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
        selectStatement = ("delete from %s;" % tableName)
        try:
            cur = self._dbconnection.cursor()
            result = self.__execute_sql(cur, selectStatement)
            if result is not None:
                return result.fetchall()
            self._dbconnection.commit()
        finally :
            if cur :
                self._dbconnection.rollback() 

    def execute_sql_script(self, sqlScriptFileName):
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
        delete from person_employee_table;
        delete from person_table;
        delete from employee_table; 
        
        Also, the last SQL command can optionally omit its trailing semi-colon.
        
        For example:
        delete from person_employee_table;
        delete from person_table;
        delete from employee_table
        
        Given this, that means you can create spread your SQL commands in several
        lines.
        
        For example:
        delete 
          from person_employee_table;
        delete 
          from person_table;
        delete 
          from employee_table
        
        However, lines that starts with a number sign (`#`) are treated as a
        commented line. Thus, none of the contents of that line will be executed.
        
        For example:
        # Delete the bridging table first...
        delete 
          from person_employee_table;
          # ...and then the bridged tables.
        delete 
          from person_table;
        delete 
          from employee_table
        """
        sqlScriptFile = open(sqlScriptFileName)

        cur = None
        try:
            cur = self._dbconnection.cursor()        
            sqlStatement = ''
            for line in sqlScriptFile:
                line = line.strip()
                if line.startswith('#'):
                    continue
                elif line.startswith('--'):
                    continue
                
                sqlFragments = line.split(';')
                if len(sqlFragments) == 1:
                    sqlStatement += line + ' '
                else:
                    for sqlFragment in sqlFragments:
                        sqlFragment = sqlFragment.strip()
                        if len(sqlFragment) == 0:
                            continue
                    
                        sqlStatement += sqlFragment + ' '
                        
                        self.__execute_sql(cur, sqlStatement)
                        sqlStatement = ''

            sqlStatement = sqlStatement.strip()    
            if len(sqlStatement) != 0:
                self.__execute_sql(cur, sqlStatement)
                
            self._dbconnection.commit()
        finally:
            if cur :
                self._dbconnection.rollback()
                
    def execute_sql_string(self, sqlString):
        """
        Executes the sqlString as SQL commands.
        Useful to pass arguments to your sql.

        SQL commands are expected to be delimited by a semi-colon (';').

        For example:
        | Execute Sql String | delete from person_employee_table; delete from person_table |

        For example with an argument:
        | Execute Sql String | select from person where first_name = ${FIRSTNAME} |
        """
        try:
            cur = self._dbconnection.cursor()
            self.__execute_sql(cur, sqlString)
            self._dbconnection.commit()
        finally:
            if cur:
                self._dbconnection.rollback()

    def __execute_sql(self, cur, sqlStatement):
        logger.debug("Executing : %s" % sqlStatement)
        return cur.execute(sqlStatement)
