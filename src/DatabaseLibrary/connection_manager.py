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

import importlib

try:
    import ConfigParser
except:
    import configparser as ConfigParser

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
        self.db_api_module_name = None
        self.omit_trailing_semicolon = False

    def connect_to_database(self, dbapiModuleName=None, dbName=None, dbUsername=None, dbPassword=None, dbHost=None, dbPort=None, dbCharset=None, dbDriver=None, dbConfigFile=None):
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

        Example db.cfg file
        | [default]
        | dbapiModuleName=pymysqlforexample
        | dbName=yourdbname
        | dbUsername=yourusername
        | dbPassword=yourpassword
        | dbHost=yourhost
        | dbPort=yourport

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

        if dbConfigFile is None:
            dbConfigFile = "./resources/db.cfg"
        config = ConfigParser.ConfigParser()
        config.read([dbConfigFile])

        dbapiModuleName = dbapiModuleName or config.get('default', 'dbapiModuleName')
        dbName = dbName or config.get('default', 'dbName')
        dbUsername = dbUsername or config.get('default', 'dbUsername')
        dbPassword = dbPassword if dbPassword is not None else config.get('default', 'dbPassword')
        dbHost = dbHost or config.get('default', 'dbHost') or 'localhost'
        dbPort = int(dbPort or config.get('default', 'dbPort'))

        if dbapiModuleName == "excel" or dbapiModuleName == "excelrw":
            self.db_api_module_name = "pyodbc"
            db_api_2 = importlib.import_module("pyodbc")
        else:
            self.db_api_module_name = dbapiModuleName
            db_api_2 = importlib.import_module(dbapiModuleName)

        if dbapiModuleName in ["MySQLdb", "pymysql"]:
            dbPort = dbPort or 3306
            logger.info('Connecting using : %s.connect(db=%s, user=%s, passwd=***, host=%s, port=%s, charset=%s) ' % (dbapiModuleName, dbName, dbUsername, dbHost, dbPort, dbCharset))
            self._dbconnection = db_api_2.connect(db=dbName, user=dbUsername, passwd=dbPassword, host=dbHost, port=dbPort, charset='utf8mb4' or dbCharset)
        elif dbapiModuleName in ["psycopg2"]:
            dbPort = dbPort or 5432
            logger.info('Connecting using : %s.connect(database=%s, user=%s, password=***, host=%s, port=%s) ' % (dbapiModuleName, dbName, dbUsername, dbHost, dbPort))
            self._dbconnection = db_api_2.connect(database=dbName, user=dbUsername, password=dbPassword, host=dbHost, port=dbPort)
        elif dbapiModuleName in ["pyodbc", "pypyodbc"]:
            dbPort = dbPort or 1433
            dbCharset = dbCharset or 'utf8mb4'
            dbDriver = dbDriver or "{SQL Server}"
            con_str = f"DRIVER={dbDriver};DATABASE={dbName};UID={dbUsername};PWD={dbPassword};charset={dbCharset};"
            if "mysql" in dbDriver.lower():
                con_str += f"SERVER={dbHost}:{dbPort}"
            else:
                con_str += f"SERVER={dbHost},{dbPort}"
            logger.info(f'Connecting using : {dbapiModuleName}.connect({con_str.replace(dbPassword, "***")})')
            self._dbconnection = db_api_2.connect(con_str)
        elif dbapiModuleName in ["excel"]:
            logger.info(
                'Connecting using : %s.connect(DRIVER={Microsoft Excel Driver (*.xls, *.xlsx, *.xlsm, *.xlsb)};DBQ=%s;ReadOnly=1;Extended Properties="Excel 8.0;HDR=YES";)' % (
                dbapiModuleName, dbName))
            self._dbconnection = db_api_2.connect(
                'DRIVER={Microsoft Excel Driver (*.xls, *.xlsx, *.xlsm, *.xlsb)};DBQ=%s;ReadOnly=1;Extended Properties="Excel 8.0;HDR=YES";)' % (
                    dbName), autocommit=True)
        elif dbapiModuleName in ["excelrw"]:
            logger.info(
                'Connecting using : %s.connect(DRIVER={Microsoft Excel Driver (*.xls, *.xlsx, *.xlsm, *.xlsb)};DBQ=%s;ReadOnly=0;Extended Properties="Excel 8.0;HDR=YES";)' % (
                dbapiModuleName, dbName))
            self._dbconnection = db_api_2.connect(
                'DRIVER={Microsoft Excel Driver (*.xls, *.xlsx, *.xlsm, *.xlsb)};DBQ=%s;ReadOnly=0;Extended Properties="Excel 8.0;HDR=YES";)' % (
                    dbName), autocommit=True)
        elif dbapiModuleName in ["ibm_db", "ibm_db_dbi"]:
            dbPort = dbPort or 50000
            logger.info('Connecting using : %s.connect(DATABASE=%s;HOSTNAME=%s;PORT=%s;PROTOCOL=TCPIP;UID=%s;PWD=***;) ' % (dbapiModuleName, dbName, dbHost, dbPort, dbUsername))
            self._dbconnection = db_api_2.connect('DATABASE=%s;HOSTNAME=%s;PORT=%s;PROTOCOL=TCPIP;UID=%s;PWD=%s;' % (dbName, dbHost, dbPort, dbUsername, dbPassword), '', '')
        elif dbapiModuleName in ["cx_Oracle"]:
            dbPort = dbPort or 1521
            oracle_dsn =  db_api_2.makedsn(host=dbHost, port=dbPort, service_name=dbName)
            logger.info('Connecting using: %s.connect(user=%s, password=***, dsn=%s) ' % (dbapiModuleName, dbUsername, oracle_dsn))
            self._dbconnection = db_api_2.connect(user=dbUsername, password=dbPassword, dsn=oracle_dsn)
            self.omit_trailing_semicolon = True
        elif dbapiModuleName in ["oracledb"]:
            dbPort = dbPort or 1521
            oracle_connection_params =  db_api_2.ConnectParams(host=dbHost, port=dbPort, service_name=dbName)
            logger.info('Connecting using: %s.connect(user=%s, password=***, params=%s) ' % (dbapiModuleName, dbUsername, oracle_connection_params))
            self._dbconnection = db_api_2.connect(user=dbUsername, password=dbPassword, params=oracle_connection_params)
            self.omit_trailing_semicolon = True
        elif dbapiModuleName in ["teradata"]:
            dbPort = dbPort or 1025
            teradata_udaExec = db_api_2.UdaExec(appName="RobotFramework", version="1.0", logConsole=False)
            logger.info('Connecting using : %s.connect(database=%s, user=%s, password=***, host=%s, port=%s) ' % (dbapiModuleName, dbName, dbUsername, dbHost, dbPort))
            self._dbconnection = teradata_udaExec.connect(
                method="odbc",
                system=dbHost,
                database=dbName,
                username=dbUsername,
                password=dbPassword,
                host=dbHost,
                port=dbPort
            )
        elif dbapiModuleName in ["ksycopg2"]:
            dbPort = dbPort or 54321
            logger.info('Connecting using : %s.connect(database=%s, user=%s, password=***, host=%s, port=%s) ' % (
            dbapiModuleName, dbName, dbUsername, dbHost, dbPort))
            self._dbconnection = db_api_2.connect(database=dbName, user=dbUsername, password=dbPassword, host=dbHost,
                                                  port=dbPort)
        else:
            logger.info('Connecting using : %s.connect(database=%s, user=%s, password=***, host=%s, port=%s) ' % (dbapiModuleName, dbName, dbUsername, dbHost, dbPort))
            self._dbconnection = db_api_2.connect(database=dbName, user=dbUsername, password=dbPassword, host=dbHost, port=dbPort)

    def connect_to_database_using_custom_params(self, dbapiModuleName=None, db_connect_string=''):
        """
        Loads the DB API 2.0 module given `dbapiModuleName` then uses it to
        connect to the database using the map string `db_connect_string`
        (parsed as a list of named arguments).
        
        Use `connect_to_database_using_custom_connection_string` for passing
        all params in a single connection string or URI.

        Example usage:        
        | Connect To Database Using Custom Params | psycopg2 | database='my_db_test', user='postgres', password='s3cr3t', host='tiger.foobar.com', port=5432 |
        | Connect To Database Using Custom Params | jaydebeapi | 'oracle.jdbc.driver.OracleDriver', 'my_db_test', 'system', 's3cr3t' |
        | Connect To Database Using Custom Params | oracledb | user="username", password="pass", dsn="localhost/orclpdb" |
        | Connect To Database Using Custom Params | sqlite3 | database="./my_database.db", isolation_level=None |
        """
        db_api_2 = importlib.import_module(dbapiModuleName)
        self.db_api_module_name = dbapiModuleName

        db_connect_string = f'db_api_2.connect({db_connect_string})'

        connection_string_with_hidden_pass = db_connect_string
        for pass_param_name in ['pass', 'passwd', 'password', 'pwd', 'PWD']:
            splitted = connection_string_with_hidden_pass.split(pass_param_name + '=')
            if len(splitted) < 2:
                continue
            splitted = splitted[1].split(',')
            value_to_hide = splitted[0]
            connection_string_with_hidden_pass = connection_string_with_hidden_pass.replace(value_to_hide, "***")
        logger.info('Executing : Connect To Database Using Custom Params : %s.connect(%s) ' % (dbapiModuleName, connection_string_with_hidden_pass))

        self._dbconnection = eval(db_connect_string)

    def connect_to_database_using_custom_connection_string(self, dbapiModuleName=None, db_connect_string=''):
        """
        Loads the DB API 2.0 module given `dbapiModuleName` then uses it to
        connect to the database using the `db_connect_string`
        (parsed as single connection connection string or URI).
        
        Use `connect_to_database_using_custom_params` for passing
        connection params as named arguments.

        Example usage:        
        | Connect To Database Using Custom Connection String | psycopg2 | postgresql://postgres:s3cr3t@tiger.foobar.com:5432/my_db_test |
        | Connect To Database Using Custom Connection String | oracledb | username/pass@localhost:1521/orclpdb" |        
        """
        db_api_2 = importlib.import_module(dbapiModuleName)
        self.db_api_module_name = dbapiModuleName
        logger.info(f"Executing : Connect To Database Using Custom Connection String : {dbapiModuleName}.connect('{db_connect_string}')")
        self._dbconnection = db_api_2.connect(db_connect_string)

    def disconnect_from_database(self, error_if_no_connection=False):
        """
        Disconnects from the database.
        By default it's not an error if there was no open database connection -
        suitable for usage as a teardown.
        However you can enforce it using the `error_if_no_connection` parameter.

        For example:
        | Disconnect From Database | # disconnects from current connection to the database |
        """
        logger.info('Executing : Disconnect From Database')
        if self._dbconnection is None:
            log_msg = "No open database connection to close"
            if error_if_no_connection:
                raise ConnectionError(log_msg)
            logger.info(log_msg)
        else:
            self._dbconnection.close()
            self._dbconnection = None

    def set_auto_commit(self, autoCommit=True):
        """
        Turn the autocommit on the database connection ON or OFF. 
        
        The default behaviour on a newly created database connection is to automatically start a 
        transaction, which means that database actions that won't work if there is an active 
        transaction will fail. Common examples of these actions are creating or deleting a database 
        or database snapshot. By turning on auto commit on the database connection these actions 
        can be performed.
        
        Example:
        | # Default behaviour, sets auto commit to true
        | Set Auto Commit
        | # Explicitly set the desired state
        | Set Auto Commit | False
        """
        logger.info('Executing : Set Auto Commit')
        self._dbconnection.autocommit = autoCommit
