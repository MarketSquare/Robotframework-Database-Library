'''
Created on Nov 24, 2010

@author: franz
'''

class Assertion(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
    def check_if_exists_in_database(self,selectStatement):
        if not self.query(selectStatement):
            raise AssertionError("Expected to have have at least one row from '%s' "
                                 "but got 0 rows." % selectStatement)
        