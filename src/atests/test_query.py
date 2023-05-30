from operator import eq, ge, gt, le, lt
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from DatabaseLibrary import DatabaseLibrary
from DatabaseLibrary.exceptions import TechnicalTestFailure, TestFailure

HELLO = "Hello"


class FakeOperationalException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class FakeProgrammingError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


@pytest.fixture
def yield_dl() -> DatabaseLibrary:
    yield DatabaseLibrary()


def test_execute_sql(yield_dl: DatabaseLibrary):
    cursor = MagicMock()
    cursor.execute.return_value = HELLO
    assert yield_dl.execute_sql(cursor, "SELECT * FROM TABLE") == HELLO


@pytest.mark.parametrize(
    "exception", [FakeProgrammingError, FakeOperationalException, Exception]
)
def test_execute_sql_exception(yield_dl: DatabaseLibrary, exception):
    cursor = MagicMock()
    cursor.execute.side_effect = exception("unit test")
    with pytest.raises(TechnicalTestFailure) as ex:
        yield_dl.execute_sql(cursor, "SELECT * FROM TABLE")
    assert "unit test" in str(ex)


def test_execute_sql_script_no_commit_no_id(yield_dl: DatabaseLibrary):
    db_conn = MagicMock()
    rollback = MagicMock()
    cursor = MagicMock()
    executed = MagicMock()
    rollback.return_value = HELLO
    db_conn.cursor = cursor
    db_conn.rollback = rollback
    exec_sql = MagicMock()
    exec_sql.return_value = HELLO
    with patch.object(yield_dl, "_dbconnection", new=db_conn):
        with patch.object(yield_dl, "execute_sql", new=executed):
            yield_dl.execute_sql_script("sqlstatement")
    cursor.assert_called_once()
    rollback.assert_called_once()
    executed.assert_called_once()


def test_execute_sql_script_commit_no_id(yield_dl: DatabaseLibrary):
    db_conn = MagicMock()
    rollback = MagicMock()
    cursor = MagicMock()
    commit = MagicMock()
    executed = MagicMock()
    rollback.return_value = HELLO
    db_conn.cursor = cursor
    db_conn.commit = commit
    db_conn.rollback = rollback
    exec_sql = MagicMock()
    exec_sql.return_value = HELLO
    with patch.object(yield_dl, "_dbconnection", new=db_conn):
        with patch.object(yield_dl, "execute_sql", new=executed):
            yield_dl.execute_sql_script("sqlstatement", commit=True)
    cursor.assert_called_once()
    rollback.assert_called_once()
    executed.assert_called_once()
    commit.assert_called_once()


def test_execute_sql_script_commit_and_id(yield_dl: DatabaseLibrary):
    db_conn = MagicMock()
    rollback = MagicMock()
    cursor = MagicMock()
    crsr = MagicMock()
    commit = MagicMock()
    executed = MagicMock()
    last_row_id = MagicMock()
    cursor.return_value = crsr
    crsr.lastrowid = last_row_id
    rollback.return_value = HELLO
    db_conn.cursor = cursor
    db_conn.commit = commit
    db_conn.rollback = rollback
    exec_sql = MagicMock()
    exec_sql.return_value = HELLO
    with patch.object(yield_dl, "_dbconnection", new=db_conn):
        with patch.object(yield_dl, "execute_sql", new=executed):
            r = yield_dl.execute_sql_script(
                "sqlstatement", commit=True, last_row_id=True
            )
    cursor.assert_called_once()
    rollback.assert_called_once()
    executed.assert_called_once()
    commit.assert_called_once()
    assert r == last_row_id


def test_execute_sql_script_cursor_not_created(yield_dl: DatabaseLibrary):
    db_conn = MagicMock()
    db_conn.cursor.side_effect = Exception()
    with pytest.raises(TechnicalTestFailure) as ex:
        with patch.object(yield_dl, "_dbconnection", new=db_conn):
            yield_dl.execute_sql_script("sqlstatement", commit=True, last_row_id=True)
    assert "Cursor creation" in str(ex)


def test_execute_sql_script_cursor_not_executed(yield_dl: DatabaseLibrary):
    db_conn = MagicMock()
    cursor = MagicMock()
    cursor_inst = MagicMock()
    db_conn.cursor = cursor
    cursor.return_value = cursor_inst
    cursor_inst.execute.side_effect = Exception()
    with pytest.raises(TechnicalTestFailure) as ex:
        with patch.object(yield_dl, "_dbconnection", new=db_conn):
            yield_dl.execute_sql_script("sqlstatement", commit=True, last_row_id=True)
    assert "Cursor execution" in str(ex)


def test_execute_sql_script_commit_failed(yield_dl: DatabaseLibrary):
    db_conn = MagicMock()
    db_conn.commit.side_effect = Exception()
    with pytest.raises(TechnicalTestFailure) as ex:
        with patch.object(yield_dl, "_dbconnection", new=db_conn):
            yield_dl.execute_sql_script("sqlstatement", commit=True, last_row_id=True)
    assert "Database commit" in str(ex)


def test_description(yield_dl: DatabaseLibrary):
    db_conn = MagicMock()
    rollback = MagicMock()
    cursor = MagicMock()
    executed = MagicMock()
    rollback.return_value = HELLO
    cursor_inst = MagicMock()
    db_conn.cursor = cursor
    cursor.return_value = cursor_inst
    cursor_inst.description = HELLO
    db_conn.rollback = rollback
    exec_sql = MagicMock()
    exec_sql.return_value = HELLO
    with patch.object(yield_dl, "_dbconnection", new=db_conn):
        with patch.object(yield_dl, "execute_sql", new=executed):
            dsc = yield_dl.description("sqlstatement")
    cursor.assert_called_once()
    rollback.assert_called_once()
    executed.assert_called_once()
    assert dsc == list(HELLO)


def test_description_cursor_not_created(yield_dl: DatabaseLibrary):
    db_conn = MagicMock()
    db_conn.cursor.side_effect = Exception()
    with pytest.raises(TechnicalTestFailure) as ex:
        with patch.object(yield_dl, "_dbconnection", new=db_conn):
            yield_dl.description("sqlstatement")
    assert "Cursor creation" in str(ex)


def test_description_cursor_not_executed(yield_dl: DatabaseLibrary):
    db_conn = MagicMock()
    cursor = MagicMock()
    cursor_inst = MagicMock()
    db_conn.cursor = cursor
    cursor.return_value = cursor_inst
    cursor_inst.execute.side_effect = Exception()
    with pytest.raises(TechnicalTestFailure) as ex:
        with patch.object(yield_dl, "_dbconnection", new=db_conn):
            yield_dl.description("sqlstatement")
    assert "Cursor execution" in str(ex)


def test_query(yield_dl: DatabaseLibrary):
    db_conn = MagicMock()
    rollback = MagicMock()
    cursor = MagicMock()
    executed = MagicMock()
    rollback.return_value = HELLO
    cursor_inst = MagicMock()
    db_conn.cursor = cursor
    cursor.return_value = cursor_inst
    cursor_inst.fetchall.return_value = [(1,), (2,), (3,), (4,), (5,), (6,)]
    cursor_inst.description = (("column",),)
    db_conn.rollback = rollback
    with patch.object(yield_dl, "_dbconnection", new=db_conn):
        with patch.object(yield_dl, "execute_sql", new=executed):
            res = yield_dl.query("sqlstatement")
    cursor.assert_called_once()
    rollback.assert_called_once()
    executed.assert_called_once()
    assert res == [
        {"column": 1},
        {"column": 2},
        {"column": 3},
        {"column": 4},
        {"column": 5},
        {"column": 6},
    ]


def test_query_limit(yield_dl: DatabaseLibrary):
    db_conn = MagicMock()
    rollback = MagicMock()
    cursor = MagicMock()
    executed = MagicMock()
    rollback.return_value = HELLO
    cursor_inst = MagicMock()
    db_conn.cursor = cursor
    cursor.return_value = cursor_inst
    cursor_inst.fetchmany.return_value = [
        (1,),
    ]
    cursor_inst.description = (("column",),)
    db_conn.rollback = rollback
    with patch.object(yield_dl, "_get_limit", return_value=1):
        with patch.object(yield_dl, "_dbconnection", new=db_conn):
            with patch.object(yield_dl, "execute_sql", new=executed):
                res = yield_dl.query("sqlstatement")
    cursor.assert_called_once()
    rollback.assert_called_once()
    executed.assert_called_once()
    assert res == [
        {"column": 1},
    ]


def test_query_limit_result_none(yield_dl: DatabaseLibrary):
    db_conn = MagicMock()
    rollback = MagicMock()
    cursor = MagicMock()
    executed = MagicMock()
    rollback.return_value = HELLO
    cursor_inst = MagicMock()
    db_conn.cursor = cursor
    cursor.return_value = cursor_inst
    cursor_inst.fetchmany.return_value = None
    cursor_inst.description = (("column",),)
    db_conn.rollback = rollback
    with patch.object(yield_dl, "_get_limit", return_value=1):
        with patch.object(yield_dl, "_dbconnection", new=db_conn):
            with patch.object(yield_dl, "execute_sql", new=executed):
                with pytest.raises(TechnicalTestFailure) as ex:
                    res = yield_dl.query("sqlstatement")
    cursor.assert_called_once()
    rollback.assert_called_once()
    executed.assert_called_once()
    assert "could not be fetched" in str(ex)


def test_query_limit_result_empty(yield_dl: DatabaseLibrary):
    db_conn = MagicMock()
    rollback = MagicMock()
    cursor = MagicMock()
    executed = MagicMock()
    rollback.return_value = HELLO
    cursor_inst = MagicMock()
    db_conn.cursor = cursor
    cursor.return_value = cursor_inst
    cursor_inst.fetchmany.return_value = []
    cursor_inst.description = (("column",),)
    db_conn.rollback = rollback
    with patch.object(yield_dl, "_get_limit", return_value=1):
        with patch.object(yield_dl, "_dbconnection", new=db_conn):
            with patch.object(yield_dl, "execute_sql", new=executed):
                res = yield_dl.query("sqlstatement")
    cursor.assert_called_once()
    rollback.assert_called_once()
    executed.assert_called_once()
    assert res == []


def op_tests():
    results = []
    actual = 10
    for op in [eq, ge, gt, le, lt]:
        for expected in [9, 10, 11]:
            results.append((expected, actual, op, op(actual, expected)))
    return results


@pytest.mark.parametrize("expected,actual,op,result", op_tests())
def test_asserted_query(yield_dl: DatabaseLibrary, expected, actual, op, result):
    db_conn = MagicMock()
    rollback = MagicMock()
    cursor = MagicMock()
    executed = MagicMock()
    rollback.return_value = HELLO
    cursor_inst = MagicMock()
    db_conn.cursor = cursor
    cursor.return_value = cursor_inst
    cursor_inst.fetchmany.return_value = [x for x in range(actual)]
    cursor_inst.fetchone.return_value = None
    cursor_inst.description = (("column",),)
    db_conn.rollback = rollback
    with patch.object(yield_dl, "_get_limit", return_value=1):
        with patch.object(yield_dl, "_dbconnection", new=db_conn):
            with patch.object(yield_dl, "execute_sql", new=executed):
                if result:
                    yield_dl.asserted_query("sqlstatement", expected, op)
                else:
                    with pytest.raises(TestFailure):
                        yield_dl.asserted_query("sqlstatement", expected, op)
    cursor.assert_called_once()
    rollback.assert_called_once()
    executed.assert_called_once()


@pytest.mark.parametrize("expected,actual,op,result", op_tests())
def test_asserted_query_first_tup(
    yield_dl: DatabaseLibrary, expected, actual, op, result
):
    db_conn = MagicMock()
    rollback = MagicMock()
    cursor = MagicMock()
    executed = MagicMock()
    rollback.return_value = HELLO
    cursor_inst = MagicMock()
    db_conn.cursor = cursor
    cursor.return_value = cursor_inst
    cursor_inst.fetchone.return_value = (actual,)
    cursor_inst.description = (("column",),)
    db_conn.rollback = rollback
    with patch.object(yield_dl, "_get_limit", return_value=1):
        with patch.object(yield_dl, "_dbconnection", new=db_conn):
            with patch.object(yield_dl, "execute_sql", new=executed):
                if result:
                    yield_dl.asserted_query("sqlstatement", expected, op, expected)
                else:
                    with pytest.raises(TestFailure):
                        yield_dl.asserted_query("sqlstatement", expected, op, expected)
    cursor.assert_called_once()
    rollback.assert_called_once()
    executed.assert_called_once()

@pytest.mark.parametrize("input,expected_output", [
    ("1.0", 1),
    ("1", 1),
    ("1.234", 1.234),
    ("zero", "zero"),
    ("None", None),
    ("Null", None),
    ("NULL", None),
    ("REEEE", "REEEE"),
    ("True", True),
    ("FALSE", False)
], ids=["float to int", "int to int", "float to float", "string to string", "None to None", "Null to None", "NULL to None", "string to string2", "True to True", "FALSE to false"])
def test_typer(yield_dl: DatabaseLibrary, input, expected_output):
    assert expected_output == yield_dl.type_clearer(input)
