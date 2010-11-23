'''
Created on Nov 23, 2010

@author: franz
'''

class ConnectionManager(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self._dbconnection = None
        
    def connect(self, dbProvider, database, username, password):
        if dbProvider == "postgres":
            import psycopg2
            self._dbconnection = psycopg2.connect (database=database, user=username, password=password)
        else:
            raise AssertionError("The database provider '%' is not supported" % dbProvider)
        
    def disconnect(self):
        self._dbconnection.close()
        
        
        
        
        
        