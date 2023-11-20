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
from configparser import ConfigParser, NoOptionError, NoSectionError
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from robot.api import logger


@dataclass
class Connection:
    client: Any
    module_name: str


class ConnectionStore:
    def __init__(self):
        self._connections: Dict[str, Connection] = {}
        self.default_alias: str = "default"

    def register_connection(self, client: Any, module_name: str, alias: str):
        if alias in self._connections:
            if alias == self.default_alias:
                logger.warn("Overwriting not closed connection.")
            else:
                logger.warn(f"Overwriting not closed connection for alias = '{alias}'")
        self._connections[alias] = Connection(client, module_name)

    def get_connection(self, alias: Optional[str]):
        """
        Return connection with given alias.

        If alias is not provided, it will return default connection.
        If there is no default connection, it will return last opened connection.
        """
        if not self._connections:
            raise ValueError(f"No database connection is open.")
        if not alias:
            if self.default_alias in self._connections:
                return self._connections[self.default_alias]
            return list(self._connections.values())[-1]
        if alias not in self._connections:
            raise ValueError(f"Alias '{alias}' not found in existing connections.")
        return self._connections[alias]

    def pop_connection(self, alias: Optional[str]):
        if not self._connections:
            return None
        if not alias:
            alias = self.default_alias
            if alias not in self._connections:
                alias = list(self._connections.keys())[-1]
        return self._connections.pop(alias, None)

    def clear(self):
        self._connections = {}

    def switch(self, alias: str):
        if alias not in self._connections:
            raise ValueError(f"Alias '{alias}' not found in existing connections.")
        self.default_alias = alias

    def __iter__(self):
        return iter(self._connections.values())


class ConfigReader:
    def __init__(self, config_file: Optional[str], alias: str):
        if config_file is None:
            config_file = "./resources/db.cfg"
        self.alias = alias
        self.config = self._load_config(config_file)

    @staticmethod
    def _load_config(config_file: str) -> Optional[ConfigParser]:
        config_path = Path(config_file)
        if not config_path.exists():
            return None
        config = ConfigParser()
        config.read([config_path])
        return config

    def get(self, param: str) -> str:
        if self.config is None:
            raise ValueError(f"Required '{param}' parameter was not provided in keyword arguments.") from None
        try:
            return self.config.get(self.alias, param)
        except NoSectionError:
            raise ValueError(f"Configuration file does not have [{self.alias}] section.") from None
        except NoOptionError:
            raise ValueError(
                f"Required '{param}' parameter missing in both keyword arguments and configuration file."
            ) from None


class ConnectionManager:
    """
    Connection Manager handles the connection & disconnection to the database.
    """

    def __init__(self):
        self.omit_trailing_semicolon: bool = False
        self.connection_store: ConnectionStore = ConnectionStore()

    def connect_to_database(
        self,
        dbapiModuleName: Optional[str] = None,
        dbName: Optional[str] = None,
        dbUsername: Optional[str] = None,
        dbPassword: Optional[str] = None,
        dbHost: Optional[str] = None,
        dbPort: Optional[int] = None,
        dbCharset: Optional[str] = None,
        dbDriver: Optional[str] = None,
        dbConfigFile: Optional[str] = None,
        driverMode: Optional[str] = None,
        alias: str = "default",
    ):
        """
        Loads the DB API 2.0 module given ``dbapiModuleName`` then uses it to
        connect to the database using provided parameters such as ``dbName``, ``dbUsername``, and ``dbPassword``.

        Optional ``alias`` parameter can be used for creating multiple open connections, even for different databases.
        If the same alias is given twice then previous connection will be overriden.

        The ``driverMode`` is used to select the *oracledb* client mode.
        Allowed values are:
        - _thin_ (default if omitted)
        - _thick_
        - _thick,lib_dir=<PATH_TO_ORACLE_CLIENT>_

        Optionally, you can specify a ``dbConfigFile`` wherein it will load the
        alias (or alias will be "default") property values for ``dbapiModuleName``, ``dbName`` ``dbUsername``
        and ``dbPassword`` (note: specifying ``dbapiModuleName``, ``dbName``
        `dbUsername` or `dbPassword` directly will override the properties of
        the same key in `dbConfigFile`). If no `dbConfigFile` is specified, it
        defaults to `./resources/db.cfg`.

        The `dbConfigFile` is useful if you don't want to check into your SCM
        your database credentials.

        Example db.cfg file
        | [alias]
        | dbapiModuleName=pymysqlforexample
        | dbName=yourdbname
        | dbUsername=yourusername
        | dbPassword=yourpassword
        | dbHost=yourhost
        | dbPort=yourport

        Example usage:
        | # explicitly specifies all db property values |
        | Connect To Database | psycopg2 | my_db | postgres | s3cr3t | tiger.foobar.com | 5432 |
        | Connect To Database | psycopg2 | my_db | postgres | s3cr3t | tiger.foobar.com | 5432 | alias=my_alias |

        | # loads all property values from default.cfg |
        | Connect To Database | dbConfigFile=default.cfg |

        | # loads all property values from ./resources/db.cfg |
        | Connect To Database |

        | # uses explicit `dbapiModuleName` and `dbName` but uses the `dbUsername` and `dbPassword` in 'default.cfg' |
        | Connect To Database | psycopg2 | my_db_test | dbConfigFile=default.cfg |

        | # uses explicit `dbapiModuleName` and `dbName` but uses the `dbUsername` and `dbPassword` in './resources/db.cfg' |
        | Connect To Database | psycopg2 | my_db_test |
        """
        config = ConfigReader(dbConfigFile, alias)

        dbapiModuleName = dbapiModuleName or config.get("dbapiModuleName")
        dbName = dbName or config.get("dbName")
        dbUsername = dbUsername or config.get("dbUsername")
        dbPassword = dbPassword if dbPassword is not None else config.get("dbPassword")
        dbHost = dbHost or config.get("dbHost") or "localhost"
        dbPort = int(dbPort if dbPort is not None else config.get("dbPort"))

        if dbapiModuleName == "excel" or dbapiModuleName == "excelrw":
            db_api_module_name = "pyodbc"
            db_api_2 = importlib.import_module("pyodbc")
        else:
            db_api_module_name = dbapiModuleName
            db_api_2 = importlib.import_module(dbapiModuleName)

        if dbapiModuleName in ["MySQLdb", "pymysql"]:
            dbPort = dbPort or 3306
            logger.info(
                f"Connecting using : {dbapiModuleName}.connect("
                f"db={dbName}, user={dbUsername}, passwd=***, host={dbHost}, port={dbPort}, charset={dbCharset})"
            )
            db_connection = db_api_2.connect(
                db=dbName,
                user=dbUsername,
                passwd=dbPassword,
                host=dbHost,
                port=dbPort,
                charset="utf8mb4" or dbCharset,
            )
        elif dbapiModuleName in ["psycopg2"]:
            dbPort = dbPort or 5432
            logger.info(
                f"Connecting using : {dbapiModuleName}.connect("
                f"database={dbName}, user={dbUsername}, password=***, host={dbHost}, port={dbPort})"
            )
            db_connection = db_api_2.connect(
                database=dbName,
                user=dbUsername,
                password=dbPassword,
                host=dbHost,
                port=dbPort,
            )
        elif dbapiModuleName in ["pyodbc", "pypyodbc"]:
            dbPort = dbPort or 1433
            dbCharset = dbCharset or "utf8mb4"
            dbDriver = dbDriver or "{SQL Server}"
            con_str = f"DRIVER={dbDriver};DATABASE={dbName};UID={dbUsername};PWD={dbPassword};charset={dbCharset};"
            if "mysql" in dbDriver.lower():
                con_str += f"SERVER={dbHost}:{dbPort}"
            else:
                con_str += f"SERVER={dbHost},{dbPort}"
            logger.info(f'Connecting using : {dbapiModuleName}.connect({con_str.replace(dbPassword, "***")})')
            db_connection = db_api_2.connect(con_str)
        elif dbapiModuleName in ["excel"]:
            logger.info(
                f"Connecting using : {dbapiModuleName}.connect("
                f"DRIVER={{Microsoft Excel Driver (*.xls, *.xlsx, *.xlsm, *.xlsb)}};DBQ={dbName};"
                f'ReadOnly=1;Extended Properties="Excel 8.0;HDR=YES";)'
            )
            db_connection = db_api_2.connect(
                f"DRIVER={{Microsoft Excel Driver (*.xls, *.xlsx, *.xlsm, *.xlsb)}};DBQ={dbName};"
                f'ReadOnly=1;Extended Properties="Excel 8.0;HDR=YES";)',
                autocommit=True,
            )
        elif dbapiModuleName in ["excelrw"]:
            logger.info(
                f"Connecting using : {dbapiModuleName}.connect("
                f"DRIVER={{Microsoft Excel Driver (*.xls, *.xlsx, *.xlsm, *.xlsb)}};DBQ={dbName};"
                f'ReadOnly=0;Extended Properties="Excel 8.0;HDR=YES";)',
            )
            db_connection = db_api_2.connect(
                f"DRIVER={{Microsoft Excel Driver (*.xls, *.xlsx, *.xlsm, *.xlsb)}};DBQ={dbName};"
                f'ReadOnly=0;Extended Properties="Excel 8.0;HDR=YES";)',
                autocommit=True,
            )
        elif dbapiModuleName in ["ibm_db", "ibm_db_dbi"]:
            dbPort = dbPort or 50000
            conn_str = f"DATABASE={dbName};HOSTNAME={dbHost};PORT={dbPort};PROTOCOL=TCPIP;UID={dbUsername};"
            logger.info(f"Connecting using : {dbapiModuleName}.connect(" f"{conn_str};PWD=***;)")
            db_connection = db_api_2.connect(
                f"{conn_str};PWD={dbPassword};",
                "",
                "",
            )
        elif dbapiModuleName in ["cx_Oracle"]:
            dbPort = dbPort or 1521
            oracle_dsn = db_api_2.makedsn(host=dbHost, port=dbPort, service_name=dbName)
            logger.info(
                f"Connecting using: {dbapiModuleName}.connect(user={dbUsername}, password=***, dsn={oracle_dsn})"
            )
            db_connection = db_api_2.connect(user=dbUsername, password=dbPassword, dsn=oracle_dsn)
            self.omit_trailing_semicolon = True
        elif dbapiModuleName in ["oracledb"]:
            dbPort = dbPort or 1521
            driverMode = driverMode or "thin"
            oracle_connection_params = db_api_2.ConnectParams(host=dbHost, port=dbPort, service_name=dbName)
            if "thick" in driverMode.lower():
                logger.info("Using thick Oracle client mode")
                mode_param = driverMode.lower().split(",lib_dir=")
                if len(mode_param) == 2 and mode_param[0].lower() == "thick":
                    lib_dir = mode_param[1]
                    logger.info(f"Oracle client lib dir specified: {lib_dir}")
                    db_api_2.init_oracle_client(lib_dir=lib_dir)
                else:
                    logger.info("No Oracle client lib dir specified, oracledb will search it in usual places")
                    db_api_2.init_oracle_client()
                oracle_thin_mode = False
            elif "thin" in driverMode.lower():
                oracle_thin_mode = True
                logger.info("Using thin Oracle client mode")
            else:
                raise ValueError(f"Invalid Oracle client mode provided: {driverMode}")
            logger.info(
                f"Connecting using: {dbapiModuleName}.connect("
                f"user={dbUsername}, password=***, params={oracle_connection_params})"
            )
            db_connection = db_api_2.connect(user=dbUsername, password=dbPassword, params=oracle_connection_params)
            assert db_connection.thin == oracle_thin_mode, (
                "Expected oracledb to run in thin mode: {oracle_thin_mode}, "
                f"but the connection has thin mode: {db_connection.thin}"
            )
            self.omit_trailing_semicolon = True
        elif dbapiModuleName in ["teradata"]:
            dbPort = dbPort or 1025
            teradata_udaExec = db_api_2.UdaExec(appName="RobotFramework", version="1.0", logConsole=False)
            logger.info(
                f"Connecting using : {dbapiModuleName}.connect("
                f"database={dbName}, user={dbUsername}, password=***, host={dbHost}, port={dbPort})"
            )
            db_connection = teradata_udaExec.connect(
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
                f"Connecting using : {dbapiModuleName}.connect("
                f"database={dbName}, user={dbUsername}, password=***, host={dbHost}, port={dbPort})"
            )
            db_connection = db_api_2.connect(
                database=dbName,
                user=dbUsername,
                password=dbPassword,
                host=dbHost,
                port=dbPort,
            )
        else:
            logger.info(
                f"Connecting using : {dbapiModuleName}.connect("
                f"database={dbName}, user={dbUsername}, password=***, host={dbHost}, port={dbPort}) "
            )
            db_connection = db_api_2.connect(
                database=dbName,
                user=dbUsername,
                password=dbPassword,
                host=dbHost,
                port=dbPort,
            )
        self.connection_store.register_connection(db_connection, db_api_module_name, alias)

    def connect_to_database_using_custom_params(
        self, dbapiModuleName: Optional[str] = None, db_connect_string: str = "", alias: str = "default"
    ):
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
        db_api_module_name = dbapiModuleName

        db_connect_string = f"db_api_2.connect({db_connect_string})"

        connection_string_with_hidden_pass = db_connect_string
        for pass_param_name in ["pass", "passwd", "password", "pwd", "PWD"]:
            splitted = connection_string_with_hidden_pass.split(pass_param_name + "=")
            if len(splitted) < 2:
                continue
            splitted = splitted[1].split(",")
            value_to_hide = splitted[0]
            connection_string_with_hidden_pass = connection_string_with_hidden_pass.replace(value_to_hide, "***")
        logger.info(
            f"Executing : Connect To Database Using Custom Params : {dbapiModuleName}.connect("
            f"{connection_string_with_hidden_pass})"
        )

        db_connection = eval(db_connect_string)
        self.connection_store.register_connection(db_connection, db_api_module_name, alias)

    def connect_to_database_using_custom_connection_string(
        self, dbapiModuleName: Optional[str] = None, db_connect_string: str = "", alias: str = "default"
    ):
        """
        Loads the DB API 2.0 module given `dbapiModuleName` then uses it to
        connect to the database using the `db_connect_string`
        (parsed as single connection string or URI).

        Use `connect_to_database_using_custom_params` for passing
        connection params as named arguments.

        Example usage:
        | Connect To Database Using Custom Connection String | psycopg2 | postgresql://postgres:s3cr3t@tiger.foobar.com:5432/my_db_test |
        | Connect To Database Using Custom Connection String | oracledb | username/pass@localhost:1521/orclpdb |
        """
        db_api_2 = importlib.import_module(dbapiModuleName)
        db_api_module_name = dbapiModuleName
        logger.info(
            f"Executing : Connect To Database Using Custom Connection String : {dbapiModuleName}.connect("
            f"'{db_connect_string}')"
        )
        db_connection = db_api_2.connect(db_connect_string)
        self.connection_store.register_connection(db_connection, db_api_module_name, alias)

    def disconnect_from_database(self, error_if_no_connection: bool = False, alias: Optional[str] = None):
        """
        Disconnects from the database.

        By default, it's not an error if there was no open database connection -
        suitable for usage as a teardown.
        However, you can enforce it using the `error_if_no_connection` parameter.

        Example usage:
        | Disconnect From Database | # disconnects from current connection to the database |
        | Disconnect From Database | alias=my_alias | # disconnects from current connection to the database |
        """
        logger.info("Executing : Disconnect From Database")
        db_connection = self.connection_store.pop_connection(alias)
        if db_connection is None:
            log_msg = "No open database connection to close"
            if error_if_no_connection:
                raise ConnectionError(log_msg) from None
            logger.info(log_msg)
        else:
            db_connection.client.close()

    def disconnect_from_all_databases(self):
        """
        Disconnects from all the databases -
        useful when testing with multiple database connections (aliases).

        For example:
        | Disconnect From All Databases | # Closes connections to all databases |
        """
        logger.info("Executing : Disconnect From All Databases")
        for db_connection in self.connection_store:
            db_connection.client.close()
        self.connection_store.clear()

    def set_auto_commit(self, autoCommit: bool = True, alias: Optional[str] = None):
        """
        Turn the autocommit on the database connection ON or OFF.

        The default behaviour on a newly created database connection is to automatically start a
        transaction, which means that database actions that won't work if there is an active
        transaction will fail. Common examples of these actions are creating or deleting a database
        or database snapshot. By turning on auto commit on the database connection these actions
        can be performed.

        Example usage:
        | # Default behaviour, sets auto commit to true
        | Set Auto Commit
        | Set Auto Commit | alias=my_alias |
        | # Explicitly set the desired state
        | Set Auto Commit | False
        """
        logger.info("Executing : Set Auto Commit")
        db_connection = self.connection_store.get_connection(alias)
        db_connection.client.autocommit = autoCommit

    def switch_database(self, alias: str):
        """
        Switch the default database connection to ``alias``.

        Examples:
        | Switch Database | my_alias |
        | Switch Database | alias=my_alias |
        """
        self.connection_store.switch(alias)
