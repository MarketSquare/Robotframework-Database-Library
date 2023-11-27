from unittest.mock import MagicMock, patch

from DatabaseLibrary import DatabaseLibrary, utils

from .mocks import ModuleMock

CONN_PARAMS = {
    "dbapiModuleName": "my_client",
    "dbName": "name",
    "dbUsername": "name",
    "dbPassword": "password",
    "dbHost": "host",
    "dbPort": 0,
}
QUERY = "SELECT * FROM users"
QUERY_RESULT = [
    {"name": "Anne", "age": 3, "city": "New York"},
    {"name": "Tom", "age": 52, "city": "Lisbon"},
    {"name": "Naomi", "age": 17, "city": "Sydney"},
]


class TestLogQueryResults:
    def test_table_to_html(self):
        exptected_html = """
        <table id="table_1983"><caption>Query results</caption>
        <thead>
            <tr><th>name</th><th>age</th><th>city</th></tr>
        </thead>
        <tbody>
            <tr><td>Anne</td><td>3</td><td>New York</td></tr>
            <tr><td>Tom</td><td>52</td><td>Lisbon</td></tr>
            <tr><td>Naomi</td><td>17</td><td>Sydney</td></tr>
        </tbody></table>
        """
        with patch("DatabaseLibrary.utils.uuid", new=MagicMock()) as uuid_mock:
            uuid_mock.uuid4.return_value = "1234-1234-1234-1983"
            exptected_html = exptected_html.replace("    ", "").replace("\n", "")
            assert exptected_html in utils.table_to_html(QUERY_RESULT)

    def test_default_no_log(self, capsys):
        library = DatabaseLibrary()
        with patch("importlib.import_module", new=ModuleMock(QUERY_RESULT)):
            library.connect_to_database(**CONN_PARAMS)
            result = library.query(QUERY, returnAsDict=True)
            assert result == QUERY_RESULT
        out, _ = capsys.readouterr()
        assert "<table>" not in out

    def test_log_table(self):
        library = DatabaseLibrary()
        html_result = utils.table_to_html(QUERY_RESULT)
        with patch("DatabaseLibrary.utils.logger", new=MagicMock()) as logger_mock, patch(
            "importlib.import_module", new=ModuleMock(QUERY_RESULT)
        ):
            library.connect_to_database(**CONN_PARAMS)
            result = library.query(QUERY, returnAsDict=True, log_results=True)
            assert result == QUERY_RESULT
        logger_mock.info.assert_called_with(html_result, html=True)
