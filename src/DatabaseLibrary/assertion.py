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

class Assertion(object):
    """
    Assertion handles all the assertions of Database Library.
    """

    def check_if_exists_in_database(self,selectStatement):
        """
        Check if any row would be returned by given the input 
        `selectStatement`. If there are no results, then this will 
        throw an AssertionError.
        
        For example, given we have a table `person` with the following data:
        | id | first_name  | last_name |
        |  1 | Franz Allan | See       |
        
        When you have the following assertions in your robot
        | Check If Exists In Database | select id from person where first_name = 'Franz Allan' |
        | Check If Exists In Database | select id from person where first_name = 'John' |
        
        Then you will get the following:
        | Check If Exists In Database | select id from person where first_name = 'Franz Allan' | # PASS |
        | Check If Exists In Database | select id from person where first_name = 'John' | # FAIL |          
        """
        if not self.query(selectStatement):
            raise AssertionError("Expected to have have at least one row from '%s' "
                                 "but got 0 rows." % selectStatement)
            
    def check_if_not_exists_in_database(self,selectStatement):
        """
        This is the negation of `check_if_exists_in_database`.
        
        Check if no rows would be returned by given the input 
        `selectStatement`. If there are any results, then this will 
        throw an AssertionError.
        
        For example, given we have a table `person` with the following data:
        | id | first_name  | last_name |
        |  1 | Franz Allan | See       |
        
        When you have the following assertions in your robot
        | Check If Not Exists In Database | select id from person where first_name = 'John' |
        | Check If Not Exists In Database | select id from person where first_name = 'Franz Allan' |
        
        Then you will get the following:
        | Check If Not Exists In Database | select id from person where first_name = 'John' | # PASS |          
        | Check If Not Exists In Database | select id from person where first_name = 'Franz Allan' | # FAIL |
        """
        queryResults = self.query(selectStatement) 
        if queryResults:
            raise AssertionError("Expected to have have no rows from '%s' "
                                 "but got some rows : %s." % (selectStatement, queryResults))

    def row_count_is_0(self,fromClause,whereClause=None):
        """
        Check if any rows are returned from the submitted `fromClause` and `whereclause`.
        If there are, then this will throw an AssertionError.
        
        For example, given we have a table `person` with the following data:
        | id | first_name  | last_name |
        |  1 | Franz Allan | See       |
        
        When you have the following assertions in your robot
        | Row Count is 0 | person | first_name = 'Franz Allan' |
        | Row Count is 0 | person | first_name = 'John' |
        
        Then you will get the following:
        | Row Count is 0 | select count(1) from person where first_name = 'Franz Allan' | # FAIL |
        | Row Count is 0 | select count(1) from person where first_name = 'John' | # PASS |          
        """
        num_rows = self.row_count(fromClause,whereClause)
        if (num_rows > 0):
            raise AssertionError("Expected zero rows to be returned but got %s rows back." % (num_rows))

    def row_count_is_equal_to_x(self,numRows,fromClause,whereClause=None):
        """
        Check if the number of rows returned from `fromClause` and `whereclause` is equal to
        the value submitted. If not, then this will throw an AssertionError.
        
        For example, given we have a table `person` with the following data:
        | id | first_name  | last_name |
        |  1 | Franz Allan | See       |
        |  2 | Jerry       | Schneider |
        
        When you have the following assertions in your robot
        | Row Count Is Equal To X | 1 | person |
        | Row Count Is Equal To X | 0 | person | first_name = 'John' |
        
        Then you will get the following:
        | Row Count Is Equal To X | 1 | select count(1) from person | # FAIL |
        | Row Count Is Equal To X | 0 | select count(1) from person where first_name = 'John' | # PASS |
        """
        num_rows = self.row_count(fromClause,whereClause)
        if (num_rows != int(numRows.encode('ascii'))):
            raise AssertionError("Expected %s row(s) to be returned but got %s row(s) back" % (numRows, num_rows))

    def row_count_is_greater_than_x(self,numRows,fromClause,whereClause=None):
        """
        Check if the number of rows returned from `fromClause` and `whereclause` is greater
        than the value submitted. If not, then this will throw an AssertionError.
        
        For example, given we have a table `person` with the following data:
        | id | first_name  | last_name |
        |  1 | Franz Allan | See       |
        |  2 | Jerry       | Schneider |
        
        When you have the following assertions in your robot
        | Row Count Is Greater Than X | 1 | person |
        | Row Count Is Greater Than X | 0 | person | first_name = 'John' |
        
        Then you will get the following:
        | Row Count Is Greater Than X | 1 | select count(1) from person | # PASS |
        | Row Count Is Greater Than X | 0 | select count(1) from person where first_name = 'John' | # FAIL |          
        """
        num_rows = self.row_count(fromClause,whereClause)
        if (num_rows <= int(numRows.encode('ascii'))):
            raise AssertionError("Expected more than %s row(s) to be returned but got %s row(s) back" % (numRows, num_rows))

    def row_count_is_less_than_x(self,numRows,fromClause,whereClause=None):
        """
        Check if the number of rows returned from `fromClause` and `whereclause` is less
        than the value submitted. If not, then this will throw an AssertionError.
        
        For example, given we have a table `person` with the following data:
        | id | first_name  | last_name |
        |  1 | Franz Allan | See       |
        |  2 | Jerry       | Schneider |
        
        When you have the following assertions in your robot
        | Row Count Is Less Than X | 3 | person |
        | Row Count Is Less Than X | 1 | person | first_name = 'John' |
        
        Then you will get the following:
        | Row Count Is Less Than X | 3 | select count(1) from person | # PASS |
        | Row Count Is Less Than X | 1 | select count(1) from person where first_name = 'John' | # FAIL |          
        """
        num_rows = self.row_count(fromClause,whereClause)
        if (num_rows >= int(numRows.encode('ascii'))):
            raise AssertionError("Expected less than %s row(s) to be returned but got %s row(s) back" % (numRows, num_rows))
                                 
    def table_must_exist(self,tableName):
        """
        Check if the table given exists in the database.
        
        For example, given we have a table `person` in a database
        
        When you do the following:
        | Table Must Exist | person |

        Then you will get the following:
        | Table Must Exist | person | # PASS |
        | Table Must Exist | first_name | # FAIL |
        """
        selectStatement = ("select * from information_schema.tables where table_name='%s'" % tableName)
        num_rows = self.row_count(selectStatement)
        if (num_rows == 0):
            raise AssertionError("Table '%s' does not exist in the db" % tableName)


