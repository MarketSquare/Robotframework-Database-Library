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
import os
from configparser import ConfigParser, NoOptionError, NoSectionError
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from robot.api import logger

from .params_decorator import renamed_args


@dataclass
class Connection:
    client: Any
    module_name: str
    omit_trailing_semicolon: bool


class ConnectionStore:
    def __init__(self, warn_on_overwrite=True):
        self._connections: Dict[str, Connection] = {}
        self.default_alias: str = "default"
        self.warn_on_overwrite = warn_on_overwrite

    def register_connection(self, client: Any, module_name: str, alias: str, omit_trailing_semicolon=False):
        if alias in self._connections and self.warn_on_overwrite:
            if alias == self.default_alias:
                logger.warn("Overwriting not closed connection.")
            else:
                logger.warn(f"Overwriting not closed connection for alias = '{alias}'")
        self._connections[alias] = Connection(client, module_name, omit_trailing_semicolon)

    def get_connection(self, alias: Optional[str]) -> Connection:
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

    def pop_connection(self, alias: Optional[str]) -> Connection:
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

    def __init__(self, warn_on_connection_overwrite=True):
        self.connection_store: ConnectionStore = ConnectionStore(warn_on_overwrite=warn_on_connection_overwrite)
        self.ibmdb_driver_already_added_to_path: bool = False

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

    @renamed_args(
        mapping={
            "dbapiModuleName": "db_module",
            "dbName": "db_name",
            "dbUsername": "db_user",
            "dbPassword": "db_password",
            "dbHost": "db_host",
            "dbPort": "db_port",
            "dbCharset": "db_charset",
            "dbDriver": "odbc_driver",
            "dbConfigFile": "config_file",
            "driverMode": "oracle_driver_mode",
        }
    )
    def connect_to_database(
        self,
        db_module: Optional[str] = None,
        db_name: Optional[str] = None,
        db_user: Optional[str] = None,
        db_password: Optional[str] = None,
        db_host: Optional[str] = None,
        db_port: Optional[int] = None,
        db_charset: Optional[str] = None,
        odbc_driver: Optional[str] = None,
        config_file: Optional[str] = None,
        oracle_driver_mode: Optional[str] = None,
        alias: str = "default",
        **custom_connection_params,
    ):
        """
        Creates a database connection using the DB API 2.0 ``db_module`` and the parameters provided.
        Along with listed commonly used arguments (`db_name`, `db_host` etc.)
        you can set any other DB module specific parameters as key/value pairs.

        Use ``config_file`` to provide a path to configuration file with connection parameters
        to be used along with / instead of keyword arguments.
        If no specified, it defaults to `./resources/db.cfg`.
        See `Using configuration file` for more details.

        All params are optional, although ``db_module`` must be set - either as keyword argument or in config file.
        If some of the listed keyword arguments (`db_name`, `db_host` etc.) are not provided (i.e. left on default value `None`),
        they are normally not passed to the Python DB module at all, except:
        - _db_port_ - commonly used port number for known databases is set as fallback
        - _db_charset_ - _UTF8_ is used as fallback for _pymysql_, _pymssql_ and _pyodbc_
        - _oracle_driver_mode_ - _thin_ is used as fallback for _oracledb_

        Other custom params from keyword arguments and config file are passed to the Python DB module as provided -
        normally as arguments for the _connect()_ function.
        However, when using *pyodbc* or *ibm_db_dbi*, the connection is established using a *connection string* -
        so all the custom params are added into it instead of function arguments.

        Set ``alias`` for `Handling multiple database connections`.
        If the same alias is given twice, then previous connection will be overridden.

        The ``oracle_driver_mode`` is used to select the *oracledb* client mode.
        Allowed values are:
        - _thin_ (default if omitted)
        - _thick_
        - _thick,lib_dir=<PATH_TO_ORACLE_CLIENT>_

        By default, there is a warning when overwriting an existing connection (i.e. not closing it properly).
        This can be disabled by setting the ``warn_on_connection_overwrite`` parameter to *False* in the library import.

        === Some parameters were renamed in version 2.0 ===
        The old parameters ``dbapiModuleName``, ``dbName``, ``dbUsername``,
        ``dbPassword``, ``dbHost``, ``dbPort``, ``dbCharset``, ``dbDriver``,
        ``dbConfigFile`` and ``driverMode`` are *deprecated*,
        please use new parameters ``db_module``, ``db_name``, ``db_user``,
        ``db_password``, ``db_host``, ``db_port``, ``db_charset``, ``odbc_driver``,
        ``config_file`` and ``oracle_driver_mode`` instead.

        *The old parameters will be removed in future versions.*

        == Basic examples ==
        | Connect To Database | psycopg2 | my_db | user | pass | 127.0.0.1 | 5432 |
        | Connect To Database | psycopg2 | my_db | user | pass | 127.0.0.1 | 5432 | my_custom_param=value |
        | Connect To Database | psycopg2 | my_db | user | pass | 127.0.0.1 | 5432 | alias=my_alias |
        | Connect To Database | config_file=my_db_params.cfg |

        See `Connection examples for different DB modules`.
        """
        config = ConfigReader(config_file, alias)

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
            connection_object = connection_object or db_module
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
            if db_password:
                msg = msg.replace(f"'{db_password}'", "***")
            msg = self._hide_password_values(msg, params_separator)
            msg = msg.replace("connect(, ", "connect(")
            msg += ")"
            logger.info(msg)

        def _arg_or_config(arg_value, param_name, *, old_param_name=None, mandatory=False):
            val_from_config = config.pop(param_name)

            # support deprecated old param names
            if val_from_config is None and old_param_name is not None:
                val_from_config = config.pop(old_param_name)
                if val_from_config is not None:
                    logger.warn(f"Config file: argument '{old_param_name}' is deprecated, use '{param_name}' instead")

            if arg_value is not None:
                final_value = arg_value
                if val_from_config is not None:
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
        db_module = _arg_or_config(db_module, "db_module", mandatory=True, old_param_name="dbapiModuleName")
        # optional named params - named because of custom module specific handling
        db_name = _arg_or_config(db_name, "db_name", old_param_name="dbName")
        db_user = _arg_or_config(db_user, "db_user", old_param_name="dbUsername")
        db_password = _arg_or_config(db_password, "db_password", old_param_name="dbPassword")
        db_host = _arg_or_config(db_host, "db_host", old_param_name="dbHost")
        db_port = _arg_or_config(db_port, "db_port", old_param_name="dbPort")
        if db_port is not None:
            db_port = int(db_port)
        db_charset = _arg_or_config(db_charset, "db_charset", old_param_name="dbCharset")
        odbc_driver = _arg_or_config(odbc_driver, "odbc_driver", old_param_name="dbDriver")
        oracle_driver_mode = _arg_or_config(oracle_driver_mode, "oracle_driver_mode", old_param_name="driverMode")

        for param_name, param_value in custom_connection_params.items():
            _arg_or_config(param_value, param_name)
        other_config_file_params = config.get_all_available_params()
        if other_config_file_params:
            logger.info(f"Other params from configuration file: {list(other_config_file_params.keys())}")

        omit_trailing_semicolon = False

        if db_module == "excel" or db_module == "excelrw":
            db_api_module_name = "pyodbc"
        else:
            db_api_module_name = db_module

        if db_api_module_name in ["ibm_db", "ibm_db_dbi"]:
            if os.name == "nt":
                if not self.ibmdb_driver_already_added_to_path:
                    spec = importlib.util.find_spec(db_api_module_name)
                    if spec is not None:
                        logger.info(
                            f"Importing DB module '{db_api_module_name}' on Windows requires configuring the DLL directory for CLI driver"
                        )
                        site_packages_path = os.path.dirname(spec.origin)
                        clidriver_bin_path = os.path.join(site_packages_path, "clidriver", "bin")
                        if os.path.exists(clidriver_bin_path):
                            os.add_dll_directory(clidriver_bin_path)
                            self.ibmdb_driver_already_added_to_path = True
                            logger.info(f"Added default CLI driver location to DLL search path: '{clidriver_bin_path}'")
                        else:
                            logger.info(f"Default CLI driver location folder not found: '{clidriver_bin_path}'")

        db_api_2 = importlib.import_module(db_api_module_name)

        if db_module in ["MySQLdb", "pymysql"]:
            db_port = db_port or 3306
            db_charset = db_charset or "utf8mb4"
            con_params = _build_connection_params(
                db=db_name, user=db_user, passwd=db_password, host=db_host, port=db_port, charset=db_charset
            )
            _log_all_connection_params(**con_params)
            db_connection = db_api_2.connect(**con_params)

        elif db_module in ["pymssql"]:
            db_port = db_port or 1433
            db_charset = db_charset or "UTF-8"
            con_params = _build_connection_params(
                database=db_name, user=db_user, password=db_password, host=db_host, port=db_port, charset=db_charset
            )
            _log_all_connection_params(**con_params)
            db_connection = db_api_2.connect(**con_params)

        elif db_module in ["psycopg2"]:
            db_port = db_port or 5432
            con_params = _build_connection_params(
                database=db_name, user=db_user, password=db_password, host=db_host, port=db_port
            )
            _log_all_connection_params(**con_params)
            db_connection = db_api_2.connect(**con_params)

        elif db_module in ["pyodbc", "pypyodbc"]:
            db_port = db_port or 1433
            db_charset = db_charset or "utf8mb4"

            if odbc_driver:
                con_str = f"DRIVER={odbc_driver};"
            else:
                con_str = ""
                logger.info("No ODBC driver specified")
                logger.info(f"List of installed ODBC drivers: {db_api_2.drivers()}")
            if db_name:
                con_str += f"DATABASE={db_name};"
            if db_user:
                con_str += f"UID={db_user};"
            if db_password:
                con_str += f"PWD={db_password};"
            if db_charset:
                con_str += f"charset={db_charset};"
            if db_host and db_port:
                con_str_server = f"SERVER={db_host},{db_port};"  # default for most databases
                if odbc_driver:
                    driver_lower = odbc_driver.lower()
                    if "mysql" in driver_lower:
                        con_str_server = f"SERVER={db_host}:{db_port};"
                    elif "saphana" in driver_lower or "hdbodbc" in driver_lower or "sap hana" in driver_lower:
                        con_str_server = f"SERVERNODE={db_host}:{db_port};"
                con_str += con_str_server

            for param_name, param_value in custom_connection_params.items():
                con_str += f"{param_name}={param_value};"

            for param_name, param_value in other_config_file_params.items():
                con_str += f"{param_name}={param_value};"

            _log_all_connection_params(connection_string=con_str)
            db_connection = db_api_2.connect(con_str)

        elif db_module in ["excel", "excelrw"]:
            con_str = f"DRIVER={{Microsoft Excel Driver (*.xls, *.xlsx, *.xlsm, *.xlsb)}};DBQ={db_name};"
            con_str += "ReadOnly="
            if db_module == "excel":
                con_str += "1;"
            elif db_module == "excelrw":
                con_str += "0;"
            con_str += 'Extended Properties="Excel 8.0;HDR=YES";)'
            logger.info(f"Connecting using : {db_api_module_name}.connect({con_str}, autocommit=True)")
            db_connection = db_api_2.connect(con_str, autocommit=True)

        elif db_module in ["ibm_db", "ibm_db_dbi"]:
            db_port = db_port or 50000
            con_str = ""
            if db_name:
                con_str += f"DATABASE={db_name};"
            if db_user:
                con_str += f"UID={db_user};"
            if db_password:
                con_str += f"PWD={db_password};"
            if db_host:
                con_str += f"HOSTNAME={db_host};"
            if db_port:
                con_str += f"PORT={db_port};"

            for param_name, param_value in custom_connection_params.items():
                con_str += f"{param_name}={param_value};"

            for param_name, param_value in other_config_file_params.items():
                con_str += f"{param_name}={param_value};"

            con_params = _build_connection_params(custom_params=False, user="", password="")
            _log_all_connection_params(connection_string=con_str, **con_params)
            db_connection = db_api_2.connect(con_str, **con_params)

        elif db_module in ["cx_Oracle"]:
            db_port = db_port or 1521
            oracle_dsn = db_api_2.makedsn(host=db_host, port=db_port, service_name=db_name)
            con_params = _build_connection_params(user=db_user, password=db_password, dsn=oracle_dsn)
            _log_all_connection_params(**con_params)
            db_connection = db_api_2.connect(**con_params)
            omit_trailing_semicolon = True

        elif db_module in ["oracledb"]:
            db_port = db_port or 1521
            oracle_driver_mode = oracle_driver_mode or "thin"
            oracle_connection_params = db_api_2.ConnectParams(host=db_host, port=db_port, service_name=db_name)
            if "thick" in oracle_driver_mode.lower():
                logger.info("Using thick Oracle client mode")
                mode_param = oracle_driver_mode.lower().split(",lib_dir=")
                if len(mode_param) == 2 and mode_param[0].lower() == "thick":
                    lib_dir = mode_param[1]
                    logger.info(f"Oracle client lib dir specified: {lib_dir}")
                    db_api_2.init_oracle_client(lib_dir=lib_dir)
                else:
                    logger.info("No Oracle client lib dir specified, oracledb will search it in usual places")
                    db_api_2.init_oracle_client()
                oracle_thin_mode = False
            elif "thin" in oracle_driver_mode.lower():
                oracle_thin_mode = True
                logger.info("Using thin Oracle client mode")
            else:
                raise ValueError(f"Invalid Oracle client mode provided: {oracle_driver_mode}")
            con_params = _build_connection_params(user=db_user, password=db_password, params=oracle_connection_params)
            _log_all_connection_params(**con_params)
            db_connection = db_api_2.connect(**con_params)
            assert db_connection.thin == oracle_thin_mode, (
                f"Expected oracledb to run in thin mode: {oracle_thin_mode}, "
                f"but the connection has thin mode: {db_connection.thin}"
            )
            omit_trailing_semicolon = True

        elif db_module in ["teradata"]:
            db_port = db_port or 1025
            teradata_udaExec = db_api_2.UdaExec(appName="RobotFramework", version="1.0", logConsole=False)
            con_params = _build_connection_params(
                method="odbc",
                system=db_host,
                database=db_name,
                username=db_user,
                password=db_password,
                host=db_host,
                port=db_port,
            )
            _log_all_connection_params(connection_object=f"{db_module}.UdaExec", **con_params)
            db_connection = teradata_udaExec.connect(**con_params)

        elif db_module in ["ksycopg2"]:
            db_port = db_port or 54321
            con_params = _build_connection_params(
                database=db_name, user=db_user, password=db_password, host=db_host, port=db_port
            )
            _log_all_connection_params(**con_params)
            db_connection = db_api_2.connect(**con_params)

        else:
            con_params = _build_connection_params(
                database=db_name, user=db_user, password=db_password, host=db_host, port=db_port
            )
            _log_all_connection_params(**con_params)
            db_connection = db_api_2.connect(**con_params)

        self.connection_store.register_connection(db_connection, db_api_module_name, alias, omit_trailing_semicolon)

    @renamed_args(mapping={"dbapiModuleName": "db_module"})
    def connect_to_database_using_custom_params(
        self,
        db_module: Optional[str] = None,
        db_connect_string: str = "",
        alias: str = "default",
        *,
        dbapiModuleName: Optional[str] = None,
    ):
        """
        *DEPRECATED* Use new `Connect To Database` keyword with custom parameters instead.
        The deprecated keyword will be removed in future versions.

        Loads the DB API 2.0 module given ``db_module`` then uses it to
        connect to the database using the map string ``db_connect_string``
        (parsed as a list of named arguments).

        Use `connect_to_database_using_custom_connection_string` for passing
        all params in a single connection string or URI.

        === Some parameters were renamed in version 2.0 ===
        The old parameter ``dbapiModuleName`` is *deprecated*,
        please use new parameter ``db_module`` instead.

        *The old parameter will be removed in future versions.*

        === Examples ===
        | Connect To Database Using Custom Params | psycopg2 | database='my_db_test', user='postgres', password='s3cr3t', host='tiger.foobar.com', port=5432 |
        | Connect To Database Using Custom Params | jaydebeapi | 'oracle.jdbc.driver.OracleDriver', 'my_db_test', 'system', 's3cr3t' |
        | Connect To Database Using Custom Params | oracledb | user="username", password="pass", dsn="localhost/orclpdb" |
        | Connect To Database Using Custom Params | sqlite3 | database="./my_database.db", isolation_level=None |
        """
        db_api_2 = importlib.import_module(db_module)
        db_api_module_name = db_module
        db_connect_string = f"db_api_2.connect({db_connect_string})"
        logger.info(
            f"Executing : Connect To Database Using Custom Params : {db_module}.connect("
            f"{self._hide_password_values(db_connect_string)})"
        )

        db_connection = eval(db_connect_string)
        self.connection_store.register_connection(db_connection, db_api_module_name, alias)

    @renamed_args(mapping={"dbapiModuleName": "db_module"})
    def connect_to_database_using_custom_connection_string(
        self,
        db_module: Optional[str] = None,
        db_connect_string: str = "",
        alias: str = "default",
        *,
        dbapiModuleName: Optional[str] = None,
    ):
        """
        Loads the DB API 2.0 module given ``db_module`` then uses it to
        connect to the database using the ``db_connect_string``
        (parsed as single connection string or URI).

        Use `Connect To Database` for passing custom connection params as named arguments.

        === Some parameters were renamed in version 2.0 ===
        The old parameter ``dbapiModuleName`` is *deprecated*,
        please use new parameter ``db_module`` instead.

        *The old parameter will be removed in future versions.*

        Example usage:
        | Connect To Database Using Custom Connection String | psycopg2 | postgresql://postgres:s3cr3t@tiger.foobar.com:5432/my_db_test |
        | Connect To Database Using Custom Connection String | oracledb | username/pass@localhost:1521/orclpdb |
        """
        db_api_2 = importlib.import_module(db_module)
        db_api_module_name = db_module
        logger.info(
            f"Executing : Connect To Database Using Custom Connection String : {db_module}.connect("
            f"'{db_connect_string}')"
        )
        db_connection = db_api_2.connect(db_connect_string)
        self.connection_store.register_connection(db_connection, db_api_module_name, alias)

    def disconnect_from_database(self, error_if_no_connection: bool = False, alias: Optional[str] = None):
        """
        Disconnects from the database.

        By default, it's not an error if there was no open database connection -
        suitable for usage as a teardown.
        However, you can enforce it using the ``error_if_no_connection`` parameter.

        Use ``alias`` to specify what connection should be closed if `Handling multiple database connections`.

        === Examples ===
        | Disconnect From Database |
        | Disconnect From Database | alias=postgres |
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
        """
        for db_connection in self.connection_store:
            db_connection.client.close()
        self.connection_store.clear()

    @renamed_args(mapping={"autoCommit": "auto_commit"})
    def set_auto_commit(
        self, auto_commit: bool = True, alias: Optional[str] = None, *, autoCommit: Optional[bool] = None
    ):
        """
        Explicitly sets the autocommit behavior of the database connection to ``auto_commit``.
        See `Commit behavior` for details.

        Use ``alias`` to specify what connection should be used if `Handling multiple database connections`.

        === Some parameters were renamed in version 2.0 ===
        The old parameter ``autoCommit`` is *deprecated*,
        please use new parameter ``auto_commit`` instead.

        *The old parameter will be removed in future versions.*

        === Examples ===
        | Set Auto Commit
        | Set Auto Commit | False |
        | Set Auto Commit | True  | alias=postgres |
        """
        db_connection = self.connection_store.get_connection(alias)
        if db_connection.module_name == "jaydebeapi":
            db_connection.client.jconn.setAutoCommit(auto_commit)
        elif db_connection.module_name in ["ibm_db", "ibm_db_dbi"]:
            raise ValueError(f"Setting autocommit for {db_connection.module_name} is not supported")
        else:
            db_connection.client.autocommit = auto_commit

    def switch_database(self, alias: str):
        """
        Switch the default database connection to ``alias``.

        Examples:
        | Switch Database | my_alias |
        | Switch Database | alias=my_alias |
        """
        self.connection_store.switch(alias)

    def set_omit_trailing_semicolon(self, omit_trailing_semicolon=True, alias: Optional[str] = None):
        """
        Set the ``omit_trailing_semicolon`` to control the `Omitting trailing semicolon behavior` for the connection.

        Use ``alias`` to specify what connection should be used if `Handling multiple database connections`.

        Examples:
        | Set Omit Trailing Semicolon | True |
        | Set Omit Trailing Semicolon | False | alias=my_alias |
        """
        db_connection = self.connection_store.get_connection(alias)
        db_connection.omit_trailing_semicolon = omit_trailing_semicolon
