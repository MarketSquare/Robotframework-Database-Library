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
#  limitations under the License.__version__ = '0.1'

from connection_manager import ConnectionManager
from query import Query
from assertion import Assertion

__version__ = '0.1'

class DatabaseLibrary(ConnectionManager, Query, Assertion):
    """
    Database Library contains utilities meant for Robot Framework's usage.
    
    This can allow you to query your database after an action has been made to verify the results.
    
    This is compatible* with any db2api module.
    
    `* - or at least theoretically it should be compatible. Currently tested only with psycopg2.`
    """
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

