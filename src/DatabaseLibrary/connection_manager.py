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

import ConfigParser
from robot.api import logger

class ConnectionManager(object):
    """
    Connection Manager handles the connection & disconnection to the database.
    """

    def __init__(self):
        """
        Initializes _dbconnection to None.
        """
        self._dbconnection = None
        
    def connect_to_database(self, dbapiModuleName=None, dbName=None, dbUsername=None, dbPassword=None, dbHost='localhost', dbPort="5432", dbConfigFile="./resources/db.cfg"):
        """
        Loads the DB API 2.0 module given `dbapiModuleName` then uses it to 
        connect to the database using `dbName`, `dbUsername`, and `dbPassword`.
        
        Optionally, you can specify a `dbConfigFile` wherein it will load the
        default property values for `dbapiModuleName`, `dbName` `dbUsername` 
        and `dbPassword` (note: specifying `dbapiModuleName`, `dbName` 
        `dbUsername` or `dbPassword` directly will override the properties of
        the same key in `dbConfigFile`). If no `dbConfigFile` is specified, it
        defaults to `./resources/db.cfg`. 
        
        The `dbConfigFile` is useful if you don't want to check into your SCM
        your database credentials.
        
        Example usage:
        | # explicitly specifies all db property values |
        | Connect To Database | psycopg2 | my_db | postgres | s3cr3t | tiger.foobar.com | 5432 |

        | # loads all property values from default.cfg |
        | Connect To Database | dbConfigFile=default.cfg | 
        
        | # loads all property values from ./resources/db.cfg |
        | Connect To Database |  
        
        | # uses explicit `dbapiModuleName` and `dbName` but uses the `dbUsername` and `dbPassword` in 'default.cfg' |
        | Connect To Database | psycopg2 | my_db_test | dbConfigFile=default.cfg |
        
        | # uses explicit `dbapiModuleName` and `dbName` but uses the `dbUsername` and `dbPassword` in './resources/db.cfg' |
        | Connect To Database | psycopg2 | my_db_test |    
        """
    
        config = ConfigParser.ConfigParser()
        config.read([dbConfigFile])
        
        dbapiModuleName = dbapiModuleName or config.get('default', 'dbapiModuleName')
        dbName = dbName or config.get('default', 'dbName')
        dbUsername = dbUsername or config.get('default', 'dbUsername')
        dbPassword = dbPassword or config.get('default', 'dbPassword')
        dbHost = dbHost or config.get('default', 'dbHost') or 'localhost'
        dbPort = int(dbPort or config.get('default', 'dbPort'))
        
        db_api_2 = __import__(dbapiModuleName)
        if dbapiModuleName in ["MySQLdb", "pymysql"]:
            dbPort = dbPort or 3306
            print "| Connect To Database | dbName | dbUserName | dbPassword | dbHost | dbPort |"
            print "| Connect To Database | %s | %s | %s | %s | %s |" % (dbName,dbUsername,dbPassword,dbHost,dbPort)
            logger.debug ('Connecting using : %s.connect(db=%s, user=%s, passwd=%s, host=%s, port=%s) ' % (dbapiModuleName, dbName, dbUsername, dbPassword, dbHost, dbPort))
            self._dbconnection = db_api_2.connect (db=dbName, user=dbUsername, passwd=dbPassword, host=dbHost, port=dbPort)
        elif dbapiModuleName in ["psycopg2"]:
            dbPort = dbPort or 5432            
            print "| Connect To Database | dbName | dbUserName | dbPassword | dbHost | dbPort |"
            print "| Connect To Database | %s | %s | %s | %s | %s |" % (dbName,dbUsername,dbPassword,dbHost,dbPort)
            logger.debug ('Connecting using : %s.connect(database=%s, user=%s, password=%s, host=%s, port=%s) ' % (dbapiModuleName, dbName, dbUsername, dbPassword, dbHost, dbPort))
            self._dbconnection = db_api_2.connect (database=dbName, user=dbUsername, password=dbPassword, host=dbHost, port=dbPort)
        else:
            print "| Connect To Database | dbName | dbUserName | dbPassword | dbHost | dbPort |"
            print "| Connect To Database | %s | %s | %s | %s | %s |" % (dbName,dbUsername,dbPassword,dbHost,dbPort)
            logger.debug ('Connecting using : %s.connect(database=%s, user=%s, password=%s, host=%s, port=%s) ' % (dbapiModuleName, dbName, dbUsername, dbPassword, dbHost, dbPort))
            self._dbconnection = db_api_2.connect (database=dbName, user=dbUsername, password=dbPassword, host=dbHost, port=dbPort)
            
    def connect_to_database_using_custom_params(self, dbapiModuleName=None, db_connect_string=''):
        """
        Loads the DB API 2.0 module given `dbapiModuleName` then uses it to 
        connect to the database using the map string `db_custom_param_string`.
        
        Example usage:
        | # for psycopg2 |
        | Connect To Database Using Custom Params | psycopg2 | database='my_db_test', user='postgres', password='s3cr3t', host='tiger.foobar.com', port=5432 |
        
        | # for JayDeBeApi | 
        | Connect To Database Using Custom Params | JayDeBeApi | 'oracle.jdbc.driver.OracleDriver', 'my_db_test', 'system', 's3cr3t' |
        """
        db_api_2 = __import__(dbapiModuleName)
        
        db_connect_string = 'db_api_2.connect(%s)' % db_connect_string
        
        print "| Connect To Database Using Custom Params | db_connect_string |"
        print "| Connect To Database Using Custom Params | %s |" % (db_connect_string)
        self._dbconnection = eval(db_connect_string)
        
    def connect_to_mongodb(self, dbHost='localhost', dbPort=27017, dbPoolSize=None, dbAutoStart=None, dbTimeout=None, dbSlaveOkay=False, dbNetworkTimeout=None, dbDocClass=dict, dbTZAware=False):
        """
        Loads pymongo and connects to the MongoDB host using parameters submitted.
        
        Example usage:
        | # To connect to foo.bar.org's MongoDB service on port 27017 |
        | Connect To MongoDB | foo.bar.org | ${27017} |
        
        """
        dbapiModuleName = 'pymongo'
        db_api_2 = __import__(dbapiModuleName);
        
        dbPort = int(dbPort)
        #print "host is               [ %s ]" % dbHost
        #print "port is               [ %s ]" % dbPort
        #print "pool_size is          [ %s ]" % dbPoolSize
        #print "auto_start_request is [ %s ]" % dbAutoStart
        #print "timeout is            [ %s ]" % dbTimeout
        #print "slave_okay is         [ %s ]" % dbSlaveOkay
        #print "document_class is     [ %s ]" % dbDocClass
        #print "tz_aware is           [ %s ]" % dbTZAware
        print "| Connect To MondoDB | dbHost | dbPort | dbPoolSize | dbAutoStart | dbTimeout | dbSlaveOkay | dbDocClass | dbTZAware |"
        print "| Connect To MondoDB | %s | %s | %s | %s | %s | %s | %s | %s |" % (dbHost,dbPort,dbPoolSize,dbAutoStart,dbTimeout,dbSlaveOkay,dbDocClass,dbTZAware)

        self._dbconnection = db_api_2.connection.Connection (host=dbHost, port=dbPort, pool_size=dbPoolSize, auto_start_request=dbAutoStart, timeout=dbTimeout, slave_okay=dbSlaveOkay, network_timeout=dbNetworkTimeout, document_class=dbDocClass, tz_aware=dbTZAware);
        
    def disconnect_from_database(self):
        """
        Disconnects from the database.
        
        For example:
        | Disconnect From Database | # disconnects from current connection to the database | 
        """
        print "| Disconnect From Database |"
        self._dbconnection.close()
        
    def disconnect_from_mongodb(self):
        """
        Disconnects from the MongoDB server.
        
        For example:
        | Disconnect From MongoDB | # disconnects from current connection to the MongoDB server | 
        """
        print "| Disconnect From MongoDB |"
        self._dbconnection.disconnect()
        
