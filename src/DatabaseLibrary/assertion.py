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
