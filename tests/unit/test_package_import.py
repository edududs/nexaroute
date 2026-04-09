from importlib import import_module


def test_package_imports() -> None:
    module = import_module("nexaroute")
    assert module.__name__ == "nexaroute"
