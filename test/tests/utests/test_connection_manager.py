import re
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from DatabaseLibrary.connection_manager import ConnectionManager

TEST_DATA = Path(__file__).parent / "test_data"


class TestConnectWithConfigFile:
    def test_connect_with_empty_config(self):
        conn_manager = ConnectionManager()
        config_path = str(TEST_DATA / "empty.cfg")
        with pytest.raises(
            ValueError,
            match="Required parameter 'dbapiModuleName' was not provided - neither in keyword arguments nor in config file",
        ):
            conn_manager.connect_to_database(dbConfigFile=config_path)

    def test_aliased_section(self):
        conn_manager = ConnectionManager()
        config_path = str(TEST_DATA / "alias.cfg")
        with patch("importlib.import_module", new=MagicMock()) as client:
            conn_manager.connect_to_database(
                "my_client",
                dbUsername="name",
                dbPassword="password",
                dbHost="host",
                dbPort=0,
                dbConfigFile=config_path,
                alias="alias2",
            )
            client.return_value.connect.assert_called_with(
                database="example", user="name", password="password", host="host", port=0
            )
