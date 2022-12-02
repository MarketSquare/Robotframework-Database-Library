class TechnicalTestFailure(Exception):
    """Exception returned when a non-defined behaviour ends the test case
    """

    def __init__(self, message) -> None:
        super().__init__(message)


class TestFailure(Exception):
    """Exception returned when tests end negatively
    """

    def __init__(self, message) -> None:
        super().__init__(message)
