"""
Helpers for testing the support of Robot Framework secret values.

The `Secret` type requires Robot Framework 7.4 or newer, so the tests using it must be skipped
with older Robot Framework versions. Creating the secrets here - and not in a `*** Variables ***`
section - keeps the test suites parsable with older Robot Framework versions too.
"""

try:
    from robot.api.types import Secret
except ImportError:
    Secret = None


def secret_values_supported() -> bool:
    """Returns `True` if the current Robot Framework version supports secret values."""
    return Secret is not None


def create_secret(value: str):
    """Returns the `value` encapsulated in a Robot Framework `Secret` object."""
    assert Secret is not None, "Secret values require Robot Framework 7.4 or newer"
    return Secret(value)
