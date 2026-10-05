from unittest.mock import MagicMock


def test_with_magic_mock_in() -> None:
    mock = MagicMock()
    assert mock


def prod_function_with_magic_mock_does_not_trigger_diagnostic() -> None:
    _mock = MagicMock()
