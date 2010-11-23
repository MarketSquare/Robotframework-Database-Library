'''
Created on Nov 23, 2010

@author: franz
'''

class Query(object):

    def __init__(self):
        '''
        Constructor
        '''
        
    def query(self, selectStatement):
        """Uses the input select statement to query for the values that will be returned."""
        '''raise AssertionError("Always an error. Message: '%s'." % (assertionMessage))'''
        cur = self._dbconnection.cursor()
        cur.execute (selectStatement);
        return cur.fetchall()
        