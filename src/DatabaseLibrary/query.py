'''
Created on Nov 23, 2010

@author: franz
'''

class Query(object):

    def __init__(self):
        '''
        Constructor
        '''
        
    def get_my_value(self, assertionMessage = 'You can provide an assertion message here.'):
        """Retrieves a value"""
        raise AssertionError("Always an error. Message: '%s'." % (assertionMessage)) 
        