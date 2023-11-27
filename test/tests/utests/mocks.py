from typing import Any, Dict, List, Optional

MockedData = Optional[List[Dict[str, Any]]]


class CursorMock:
    def __init__(self, data: MockedData):
        self.data = data or []

    def execute(self, *args, **kwargs):
        pass

    def fetchall(self) -> List[Any]:
        return [list(row.values()) for row in self.data]

    @property
    def description(self) -> List[List[str]]:
        return [[key] for key in self.data[0].keys()] if self.data else []


class ClientMock:
    def __init__(self, data: MockedData):
        self.data = data

    def connect(self, *args, **kwargs):
        pass

    def cursor(self, *args, **kwargs) -> CursorMock:
        return CursorMock(self.data)

    def rollback(self):
        pass

    def commit(self):
        pass

    def close(self):
        pass


class ConnectionMock:
    def __init__(self, data: MockedData):
        self.data = data

    def connect(self, *args, **kwargs):
        return ClientMock(self.data)


class ModuleMock:
    def __init__(self, data: MockedData = None):
        self.data = data

    def __call__(self, *args):
        return ConnectionMock(self.data)
