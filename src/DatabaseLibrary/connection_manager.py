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

import configparser as ConfigParser
import importlib

from func_timeout import func_set_timeout
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

    @func_set_timeout(60 * 60)
    def connect_to_snowflake(self, dbName: str, dbUsername: str, dbPassword: str, dbSchema: str, dbAccount: str, dbWarehouse: str):
        """Connect to Snowflake and set the _dbconnection object.

        Args:
            dbName (str): name of the database to connect to
            dbUsername (str): name of the user to connect as
            dbPassword (str): password for the user
            dbSchema (str): name of the schema to connect to
            dbAccount (str): name of the Snowflake Account to use
            dbWarehouse (str): name of the warehouse to connect to

        Raises:
            ImportError: Could not connect, snowflake connector is missing.
            Exception: Something unexpected happened. Could not connect.
        """           
        try:
            self.db_api_module_name = 'snowflake'
            db_api_2 = importlib.import_module("snowflake.connector")
            logger.info(
                f"Connecting using : snowflake.connector.connect(db={dbName}, user={dbUsername}, passwd={dbPassword}, account={dbAccount}, schema={dbSchema}, warehouse={dbWarehouse}) "
            )
            self._dbconnection = db_api_2.connect(
                user=dbUsername,
                password=dbPassword,
                account=dbAccount,
                warehouse=dbWarehouse,
                database=dbName,
                schema=dbSchema,
            )
        except ImportError:
            logger.error(
                "Module for connecting to Snowflake was not found. Report this to maintainers."
            )
            raise
        except Exception as ex:
            logger.error(
                f"Unexpected errors when connecting to database: {str(ex)}")
            raise

    @func_set_timeout(60 * 60)
    def connect_to_databricks(self, dbHost: str, dbToken: str, dbHttpPath: str, dbCatalog: str, dbSchema: str):
        """Connect to databricks and set the _db_connection object

        Args:
            dbHost (str): hostname to connect to
            dbToken (str): token to use for authentication
            dbHttpPath (str): http path to the sql extension
            dbCatalog (str): catalog to connect to
            dbSchema (str): schema to connect to

        Raises:
            ImportError: Could not connect, databricks connector is missing.
            Exception: Something unexpected happened. Could not connect.
        """        
        try:
            module = importlib.import_module("databricks.sql")
            logger.info(
                f"Connecting using : databricks.sql.connect(server_hostname={dbHost}, http_path={dbHttpPath}, catalog={dbCatalog}, schema={dbSchema}) "
            )
            self.db_api_module_name = 'databricks'
            self._dbconnection = module.connect(
                server_hostname=dbHost,
                access_token=dbToken,
                http_path=dbHttpPath,
                catalog=dbCatalog,
                schema=dbSchema
            )
        except ImportError:
            logger.error(
                "Module for connecting to Databricks was not found. Report this to maintainers."
            )
            raise
        except Exception as ex:
            logger.error(
                f"Unexpected errors when connecting to database: {str(ex)}")
            raise

    @func_set_timeout(60 * 60)
    def connect_to_database(
        self,
        dbapiModuleName: str = None,
        dbName: str = None,
        dbUsername: str = None,
        dbPassword: str = None,
        dbHost: str = None,
        dbPort: str = None,
        dbCharset: str = None,
        dbDriver: str = None,
        dbConfigFile: str = "./resources/db.cfg",
    ):
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
        try:
            config = ConfigParser.ConfigParser()
            config.read([dbConfigFile])

            dbapiModuleName = dbapiModuleName or config.get(
                "default", "dbapiModuleName")
            dbName = dbName or config.get("default", "dbName")
            dbUsername = dbUsername or config.get("default", "dbUsername")
            dbPassword = (
                dbPassword
                if dbPassword is not None
                else config.get("default", "dbPassword")
            )
            dbHost = dbHost or config.get("default", "dbHost") or "localhost"
            dbPort = int(dbPort or config.get("default", "dbPort"))

            if dbapiModuleName == "excel" or dbapiModuleName == "excelrw":
                self.db_api_module_name = "pyodbc"
                db_api_2 = importlib.import_module("pyodbc")
            else:
                self.db_api_module_name = dbapiModuleName
                db_api_2 = importlib.import_module(dbapiModuleName)
            if dbapiModuleName in ["MySQLdb", "pymysql"]:
                dbPort = dbPort or 3306
                logger.info(
                    "Connecting using : %s.connect(db=%s, user=%s, passwd=%s, host=%s, port=%s, charset=%s) "
                    % (
                        dbapiModuleName,
                        dbName,
                        dbUsername,
                        dbPassword,
                        dbHost,
                        dbPort,
                        dbCharset,
                    )
                )
                self._dbconnection = db_api_2.connect(
                    db=dbName,
                    user=dbUsername,
                    passwd=dbPassword,
                    host=dbHost,
                    port=dbPort,
                    charset=dbCharset,
                )
            elif dbapiModuleName in ["psycopg2"]:
                dbPort = dbPort or 5432
                logger.info(
                    "Connecting using : %s.connect(database=%s, user=%s, password=%s, host=%s, port=%s) "
                    % (dbapiModuleName, dbName, dbUsername, dbPassword, dbHost, dbPort)
                )
                self._dbconnection = db_api_2.connect(
                    database=dbName,
                    user=dbUsername,
                    password=dbPassword,
                    host=dbHost,
                    port=dbPort,
                )
            elif dbapiModuleName in ["pyodbc", "pypyodbc"]:
                dbPort = dbPort or 1433
                dbDriver = dbDriver or "{SQL Server}"
                logger.info(
                    "Connecting using : %s.connect(DRIVER=%s;SERVER=%s,%s;DATABASE=%s;UID=%s;PWD=%s)"
                    % (
                        dbapiModuleName,
                        dbDriver,
                        dbHost,
                        dbPort,
                        dbName,
                        dbUsername,
                        dbPassword,
                    )
                )
                self._dbconnection = db_api_2.connect(
                    "DRIVER=%s;SERVER=%s,%s;DATABASE=%s;UID=%s;PWD=%s"
                    % (dbDriver, dbHost, dbPort, dbName, dbUsername, dbPassword)
                )
            elif dbapiModuleName in ["excel"]:
                logger.info(
                    'Connecting using : %s.connect(DRIVER={Microsoft Excel Driver (*.xls, *.xlsx, *.xlsm, *.xlsb)};DBQ=%s;ReadOnly=1;Extended Properties="Excel 8.0;HDR=YES";)'
                    % (dbapiModuleName, dbName)
                )
                self._dbconnection = db_api_2.connect(
                    'DRIVER={Microsoft Excel Driver (*.xls, *.xlsx, *.xlsm, *.xlsb)};DBQ=%s;ReadOnly=1;Extended Properties="Excel 8.0;HDR=YES";)'
                    % (dbName),
                    autocommit=True,
                )
            elif dbapiModuleName in ["excelrw"]:
                logger.info(
                    'Connecting using : %s.connect(DRIVER={Microsoft Excel Driver (*.xls, *.xlsx, *.xlsm, *.xlsb)};DBQ=%s;ReadOnly=0;Extended Properties="Excel 8.0;HDR=YES";)'
                    % (dbapiModuleName, dbName)
                )
                self._dbconnection = db_api_2.connect(
                    'DRIVER={Microsoft Excel Driver (*.xls, *.xlsx, *.xlsm, *.xlsb)};DBQ=%s;ReadOnly=0;Extended Properties="Excel 8.0;HDR=YES";)'
                    % (dbName),
                    autocommit=True,
                )
            elif dbapiModuleName in ["ibm_db", "ibm_db_dbi"]:
                dbPort = dbPort or 50000
                logger.info(
                    "Connecting using : %s.connect(DATABASE=%s;HOSTNAME=%s;PORT=%s;PROTOCOL=TCPIP;UID=%s;PWD=%s;) "
                    % (dbapiModuleName, dbName, dbHost, dbPort, dbUsername, dbPassword)
                )
                self._dbconnection = db_api_2.connect(
                    "DATABASE=%s;HOSTNAME=%s;PORT=%s;PROTOCOL=TCPIP;UID=%s;PWD=%s;"
                    % (dbName, dbHost, dbPort, dbUsername, dbPassword),
                    "",
                    "",
                )
            elif dbapiModuleName in ["cx_Oracle"]:
                dbPort = dbPort or 1521
                oracle_dsn = db_api_2.makedsn(
                    host=dbHost, port=dbPort, service_name=dbName)
                logger.info(
                    "Connecting using: %s.connect(user=%s, password=%s, dsn=%s) "
                    % (dbapiModuleName, dbUsername, dbPassword, oracle_dsn)
                )
                self._dbconnection = db_api_2.connect(
                    user=dbUsername, password=dbPassword, dsn=oracle_dsn
                )
            elif dbapiModuleName in ["teradata"]:
                dbPort = dbPort or 1025
                teradata_udaExec = db_api_2.UdaExec(
                    appName="RobotFramework", version="1.0", logConsole=False
                )
                logger.info(
                    "Connecting using : %s.connect(database=%s, user=%s, password=%s, host=%s, port=%s) "
                    % (dbapiModuleName, dbName, dbUsername, dbPassword, dbHost, dbPort)
                )
                self._dbconnection = teradata_udaExec.connect(
                    method="odbc",
                    system=dbHost,
                    database=dbName,
                    username=dbUsername,
                    password=dbPassword,
                    host=dbHost,
                    port=dbPort,
                )
            elif dbapiModuleName in ["ksycopg2"]:
                dbPort = dbPort or 54321
                logger.info(
                    "Connecting using : %s.connect(database=%s, user=%s, password=%s, host=%s, port=%s) "
                    % (dbapiModuleName, dbName, dbUsername, dbPassword, dbHost, dbPort)
                )
                self._dbconnection = db_api_2.connect(
                    database=dbName,
                    user=dbUsername,
                    password=dbPassword,
                    host=dbHost,
                    port=dbPort,
                )
            elif dbapiModuleName in ["pymssql"]:
                # with tds_version=7.2, for pymssql driver, date/datetime values will be returned as strings
                tdsVersion = "7.2"
                logger.info(
                    "Connecting using : %s.connect(database=%s, user=%s, password=%s, host=%s, port=%s, tdsVersion=%s)"
                    % (
                        dbapiModuleName,
                        dbName,
                        dbUsername,
                        dbPassword,
                        dbHost,
                        dbPort,
                        tdsVersion,
                    )
                )
                self._dbconnection = db_api_2.connect(
                    database=dbName,
                    user=dbUsername,
                    password=dbPassword,
                    host=dbHost,
                    port=dbPort,
                    tds_version=tdsVersion,
                )
            else:
                logger.info(
                    "Connecting using : %s.connect(database=%s, user=%s, password=%s, host=%s, port=%s)"
                    % (dbapiModuleName, dbName, dbUsername, dbPassword, dbHost, dbPort)
                )
                self._dbconnection = db_api_2.connect(
                    database=dbName,
                    user=dbUsername,
                    password=dbPassword,
                    host=dbHost,
                    port=dbPort,
                )
        except Exception as ex:
            logger.error(
                f"Unexpected errors when connecting to database: {str(ex)}")
            raise

    @func_set_timeout(60 * 60)
    def connect_to_database_using_custom_params(
        self, dbapiModuleName: str = None, db_connect_string: str = ""
    ):
        """
        Loads the DB API 2.0 module given `dbapiModuleName` then uses it to
        connect to the database using the map string `db_custom_param_string`.

        Example usage:
        | # for psycopg2 |
        | Connect To Database Using Custom Params | psycopg2 | database='my_db_test', user='postgres', password='s3cr3t', host='tiger.foobar.com', port=5432 |

        | # for JayDeBeApi |
        | Connect To Database Using Custom Params | jaydebeapi | 'oracle.jdbc.driver.OracleDriver', 'my_db_test', 'system', 's3cr3t' |
        """
        db_api_2 = importlib.import_module(dbapiModuleName)

        db_connect_string = "db_api_2.connect(%s)" % db_connect_string

        self.db_api_module_name = dbapiModuleName
        logger.info(
            "Executing : Connect To Database Using Custom Params : %s.connect(%s) "
            % (dbapiModuleName, db_connect_string)
        )
        self._dbconnection = eval(db_connect_string)

    def disconnect_from_database(self):
        """
        Disconnects from the database.

        For example:
        | Disconnect From Database | # disconnects from current connection to the database |
        """
        logger.info("Executing : Disconnect From Database")
        if self._dbconnection == None:
            logger.trace("No open connection to close")
        else:
            try:
                self._dbconnection.close()
            except Exception as ex:
                logger.error(
                    f"Could not close the connection due to error: {str(ex)}. \n\nThis should not impact anything.")

    def set_auto_commit(self, autoCommit: bool = True):
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
        logger.info("Executing : Set Auto Commit")
        self._dbconnection.autocommit = autoCommit
