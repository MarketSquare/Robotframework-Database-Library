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
class Query(object):
    """
    Query handles all the querying done by the Database Library. 
    """

    def query(self, selectStatement):
        """
        Uses the input `selectStatement` to query for the values that 
        will be returned as a list of tuples.
        
        Tip: try specifying the column names in your select statements 
        as much as possible to prevent any unnecessary surprises with schema
        changes and to easily see what your [] indexing is trying to retrieve 
        (i.e. instead of `"select * from my_table"`, try 
        `"select id, col_1, col_2 from my_table"`).
        """
        cur = self._dbconnection.cursor()
        cur.execute (selectStatement);
        return cur.fetchall()
