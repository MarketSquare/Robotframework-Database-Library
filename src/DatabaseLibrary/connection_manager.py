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
        logger.info(f"Looking for configuration file: '{config_path}'")
        if not config_path.exists():
            logger.info("Configuration file doesn't exist")
            return None
        config = ConfigParser()
        config.read([config_path])
        logger.info("Successfully loaded configuration file")
        return config

    def pop(self, param: str) -> Optional[str]:
        """
        Returns the `param` value read from the config file and deletes it from the list of all params read
        """
        if self.config is None:
            logger.debug("Configuration file not loaded")
            return None
        try:
            logger.debug(f"Looking for parameter '{param}' in configuration file")
            param_value = self.config.get(self.alias, param)
            logger.info(f"Found parameter '{param}' in configuration file")
            self.config.remove_option(self.alias, param)
            return param_value
        except NoSectionError:
            logger.debug(f"Configuration file does not have [{self.alias}] section.")
        except NoOptionError:
            logger.debug(f"Parameter '{param}' missing in configuration file.")
            return None

    def get_all_available_params(self) -> Dict:
        """
        Returns a dictionary of all params read from the config file, which are currently available
        (some of them might have been removed using the `pop` function)
        """
        if self.config is None:
            logger.debug("Configuration file not loaded")
            return {}
        try:
            all_options = dict(self.config.items(self.alias))
            return all_options
        except NoSectionError:
            logger.debug(f"Configuration file does not have [{self.alias}] section.")
            return {}


class ConnectionManager:
    """
    Connection Manager handles the connection & disconnection to the database.
    """

    def __init__(self):
        self.omit_trailing_semicolon: bool = False
        self.connection_store: ConnectionStore = ConnectionStore()

    @staticmethod
    def _hide_password_values(string_with_pass, params_separator=","):
        string_with_hidden_pass = string_with_pass
        for pass_param_name in ["pass", "passwd", "password", "pwd", "PWD"]:
            pass_param_name += "="
            splitted = string_with_hidden_pass.split(pass_param_name)
            if len(splitted) < 2:
                continue
            splitted = splitted[1].split(params_separator)
            value_to_hide = splitted[0]
            string_with_hidden_pass = string_with_hidden_pass.replace(
                f"{pass_param_name}{value_to_hide}", f"{pass_param_name}***"
            )
        return string_with_hidden_pass

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
        **custom_connection_params,
    ):
        """
        Creates a database connection using the DB API 2.0 module ``dbapiModuleName`` and the parameters provided.
        Along with listed commonly used arguments (`dbName`, `dbHost` etc.)
        you can set any other DB module specific parameters as key/value pairs.

        Use ``dbConfigFile`` to provide a path to configuration file with connection parameters
        to be used along with / instead of keyword arguments.
        If no specified, it defaults to `./resources/db.cfg`.
        See `Using configuration file` for more details.

        All params are optional, although ``dbapiModuleName`` must be set - either as keyword argument or in config file.
        If some of the listed keyword arguments (`dbName`, `dbHost` etc.) are not provided (i.e. left on dafault value `None`),
        they are normally not passed to the Python DB module at all, except:
        - _dbPort_ - commonly used port number for known databases is set as fallback
        - _dbCharset_ - _UTF8_ is used as fallback for _pymysql_, _pymssql_ and _pyodbc_
        - _driverMode_ - _thin_ is used as fallback for _oracledb_

        Other custom params from keyword arguments and config file are passed to the Python DB module as provided -
        normally as arguments for the _connect()_ function. However, when using *pyodbc*, the connection is established
        using a connection string - so all the custom params are added into it instead of function arguments.

        Optional ``alias`` parameter can be used for creating multiple open connections, even for different databases.
        If the same alias is given twice then previous connection will be overridden.

        The ``driverMode`` is used to select the *oracledb* client mode.
        Allowed values are:
        - _thin_ (default if omitted)
        - _thick_
        - _thick,lib_dir=<PATH_TO_ORACLE_CLIENT>_

        Examples
        | Connect To Database | psycopg2 | my_db | user | pass | tiger.foobar.com | 5432 |
        | Connect To Database | psycopg2 | my_db | user | pass | tiger.foobar.com | 5432 | my_custom_param=value |
        | Connect To Database | psycopg2 | my_db | user | pass | tiger.foobar.com | 5432 | alias=my_alias |
        | Connect To Database | dbConfigFile=my_db_params.cfg |
        """
        config = ConfigReader(dbConfigFile, alias)

        def _build_connection_params(custom_params=True, **basic_params):
            con_params = basic_params.copy()
            for param_name, param_val in basic_params.items():
                if param_val is None:
                    con_params.pop(param_name, None)
            if custom_params:
                con_params.update(custom_connection_params)
                con_params.update(other_config_file_params)

            return con_params

        def _log_all_connection_params(*, connection_object=None, connection_string=None, **connection_params):
            connection_object = connection_object or dbapiModuleName
            msg = f"Connect to DB using : {connection_object}.connect("
            params_separator = ","
            if connection_string:
                msg += f'"{connection_string}"'
                params_separator = ";"
            for param_name, param_value in connection_params.items():
                msg += f", {param_name}="
                if isinstance(param_value, str):
                    msg += f"'{param_value}'"
                else:
                    msg += f"{param_value}"
            if dbPassword:
                msg = msg.replace(f"'{dbPassword}'", "***")
            msg = self._hide_password_values(msg, params_separator)
            msg = msg.replace("connect(, ", "connect(")
            msg += ")"
            logger.info(msg)

        def _arg_or_config(arg_value, param_name, mandatory=False):
            val_from_config = config.pop(param_name)
            if arg_value:
                final_value = arg_value
                if val_from_config:
                    logger.info(
                        f"Parameter '{param_name}' set both as keyword argument and in config file, "
                        "but keyword arguments take precedence"
                    )
            else:
                final_value = val_from_config
                if final_value is None and mandatory:
                    raise ValueError(
                        f"Required parameter '{param_name}' was not provided - "
                        "neither in keyword arguments nor in config file"
                    )
            return final_value

        # mandatory parameter
        dbapiModuleName = _arg_or_config(dbapiModuleName, "dbapiModuleName", mandatory=True)
        # optional named params - named because of custom module specific handling
        dbName = _arg_or_config(dbName, "dbName")
        dbUsername = _arg_or_config(dbUsername, "dbUsername")
        dbPassword = _arg_or_config(dbPassword, "dbPassword")
        dbHost = _arg_or_config(dbHost, "dbHost")
        dbPort = _arg_or_config(dbPort, "dbPort")
        if dbPort:
            dbPort = int(dbPort)
        dbCharset = _arg_or_config(dbCharset, "dbCharset")
        dbDriver = _arg_or_config(dbDriver, "dbDriver")
        driverMode = _arg_or_config(driverMode, "driverMode")

        for param_name, param_value in custom_connection_params.items():
            _arg_or_config(param_value, param_name)
        other_config_file_params = config.get_all_available_params()
        if other_config_file_params:
            logger.info(f"Other params from configuration file: {list(other_config_file_params.keys())}")

        if dbapiModuleName == "excel" or dbapiModuleName == "excelrw":
            db_api_module_name = "pyodbc"
        else:
            db_api_module_name = dbapiModuleName
        db_api_2 = importlib.import_module(db_api_module_name)

        if dbapiModuleName in ["MySQLdb", "pymysql"]:
            dbPort = dbPort or 3306
            dbCharset = dbCharset or "utf8mb4"
            con_params = _build_connection_params(
                db=dbName, user=dbUsername, passwd=dbPassword, host=dbHost, port=dbPort, charset=dbCharset
            )
            _log_all_connection_params(**con_params)
            db_connection = db_api_2.connect(**con_params)

        elif dbapiModuleName in ["pymssql"]:
            dbPort = dbPort or 1433
            dbCharset = dbCharset or "UTF-8"
            con_params = _build_connection_params(
                database=dbName, user=dbUsername, password=dbPassword, host=dbHost, port=dbPort, charset=dbCharset
            )
            _log_all_connection_params(**con_params)
            db_connection = db_api_2.connect(**con_params)

        elif dbapiModuleName in ["psycopg2"]:
            dbPort = dbPort or 5432
            con_params = _build_connection_params(
                database=dbName, user=dbUsername, password=dbPassword, host=dbHost, port=dbPort
            )
            _log_all_connection_params(**con_params)
            db_connection = db_api_2.connect(**con_params)

        elif dbapiModuleName in ["pyodbc", "pypyodbc"]:
            dbPort = dbPort or 1433
            dbCharset = dbCharset or "utf8mb4"

            if dbDriver:
                con_str = f"DRIVER={dbDriver};"
            else:
                con_str = ""
                logger.info("No ODBC driver specified")
                logger.info(f"List of installed ODBC drivers: {db_api_2.drivers()}")
            if dbName:
                con_str += f"DATABASE={dbName};"
            if dbUsername:
                con_str += f"UID={dbUsername};"
            if dbPassword:
                con_str += f"PWD={dbPassword};"
            if dbCharset:
                con_str += f"charset={dbCharset};"
            if dbHost and dbPort:
                if dbDriver and "mysql" in dbDriver.lower():
                    con_str += f"SERVER={dbHost}:{dbPort};"
                else:
                    con_str += f"SERVER={dbHost},{dbPort};"

            for param_name, param_value in custom_connection_params.items():
                con_str += f"{param_name}={param_value};"

            for param_name, param_value in other_config_file_params.items():
                con_str += f"{param_name}={param_value};"

            _log_all_connection_params(connection_string=con_str)
            db_connection = db_api_2.connect(con_str)

        elif dbapiModuleName in ["excel", "excelrw"]:
            con_str = f"DRIVER={{Microsoft Excel Driver (*.xls, *.xlsx, *.xlsm, *.xlsb)}};DBQ={dbName};"
            con_str += "ReadOnly="
            if dbapiModuleName == "excel":
                con_str += "1;"
            elif dbapiModuleName == "excelrw":
                con_str += "0;"
            con_str += 'Extended Properties="Excel 8.0;HDR=YES";)'
            logger.info(f"Connecting using : {db_api_module_name}.connect({con_str}, autocommit=True)")
            db_connection = db_api_2.connect(con_str, autocommit=True)

        elif dbapiModuleName in ["ibm_db", "ibm_db_dbi"]:
            dbPort = dbPort or 50000
            con_str = (
                f"DATABASE={dbName};HOSTNAME={dbHost};PORT={dbPort};PROTOCOL=TCPIP;UID={dbUsername};PWD={dbPassword};"
            )
            con_params = _build_connection_params(userID="", userPassword="")
            _log_all_connection_params(connection_string=con_str, **con_params)
            db_connection = db_api_2.connect(con_str, **con_params)

        elif dbapiModuleName in ["cx_Oracle"]:
            dbPort = dbPort or 1521
            oracle_dsn = db_api_2.makedsn(host=dbHost, port=dbPort, service_name=dbName)
            con_params = _build_connection_params(user=dbUsername, password=dbPassword, dsn=oracle_dsn)
            _log_all_connection_params(**con_params)
            db_connection = db_api_2.connect(**con_params)
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
            con_params = _build_connection_params(user=dbUsername, password=dbPassword, params=oracle_connection_params)
            _log_all_connection_params(**con_params)
            db_connection = db_api_2.connect(**con_params)
            assert db_connection.thin == oracle_thin_mode, (
                "Expected oracledb to run in thin mode: {oracle_thin_mode}, "
                f"but the connection has thin mode: {db_connection.thin}"
            )
            self.omit_trailing_semicolon = True

        elif dbapiModuleName in ["teradata"]:
            dbPort = dbPort or 1025
            teradata_udaExec = db_api_2.UdaExec(appName="RobotFramework", version="1.0", logConsole=False)
            con_params = _build_connection_params(
                method="odbc",
                system=dbHost,
                database=dbName,
                username=dbUsername,
                password=dbPassword,
                host=dbHost,
                port=dbPort,
            )
            _log_all_connection_params(connection_object=f"{dbapiModuleName}.UdaExec", **con_params)
            db_connection = teradata_udaExec.connect(**con_params)

        elif dbapiModuleName in ["ksycopg2"]:
            dbPort = dbPort or 54321
            con_params = _build_connection_params(
                database=dbName, user=dbUsername, password=dbPassword, host=dbHost, port=dbPort
            )
            _log_all_connection_params(**con_params)
            db_connection = db_api_2.connect(**con_params)

        else:
            con_params = _build_connection_params(
                database=dbName, user=dbUsername, password=dbPassword, host=dbHost, port=dbPort
            )
            _log_all_connection_params(**con_params)
            db_connection = db_api_2.connect(**con_params)

        self.connection_store.register_connection(db_connection, db_api_module_name, alias)

    def connect_to_database_using_custom_params(
        self, dbapiModuleName: Optional[str] = None, db_connect_string: str = "", alias: str = "default"
    ):
        """
        *DEPRECATED* Use new `Connect To Database` keyword with custom parameters instead.
        The deprecated keyword will be removed in future versions.

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
        logger.info(
            f"Executing : Connect To Database Using Custom Params : {dbapiModuleName}.connect("
            f"{self._hide_password_values(db_connect_string)})"
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
