__version__ = '0.1'

from connection_manager import ConnectionManager
from query import Query

class DatabaseLibrary(ConnectionManager, Query):
    """
    Contains Database utilities meant for Robot Framework's usage.
    """
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    