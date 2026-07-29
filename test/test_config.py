import pytest
from config import load_config, ConfigError


def write_config(tmp_path: object, content: str) -> str:
    """Helper: escreve um config.txt temporário e devolve o caminho."""
    path = tmp_path / "config.txt"  # type: ignore[operator]
    path.write_text(content)
    return str(path)


def test_valid_config_loads(tmp_path: object) -> None:
    path = write_config(tmp_path, """
WIDTH=10
HEIGHT=10
ENTRY=0,0
EXIT=9,9
OUTPUT_FILE=maze.txt
PERFECT=True
""")
    config = load_config(path)
    assert config["WIDTH"] == 10
    assert config["ENTRY"] == (0, 0)
    assert config["PERFECT"] is True


def test_missing_key_raises(tmp_path: object) -> None:
    path = write_config(tmp_path, "WIDTH=10\nHEIGHT=10\n")
    with pytest.raises(ConfigError):
        load_config(path)


def test_negative_width_raises(tmp_path: object) -> None:
    path = write_config(tmp_path, """
WIDTH=-5
HEIGHT=10
ENTRY=0,0
EXIT=9,9
OUTPUT_FILE=maze.txt
PERFECT=True
""")
    with pytest.raises(ConfigError):
        load_config(path)


def test_entry_equals_exit_raises(tmp_path: object) -> None:
    path = write_config(tmp_path, """
WIDTH=10
HEIGHT=10
ENTRY=0,0
EXIT=0,0
OUTPUT_FILE=maze.txt
PERFECT=True
""")
    with pytest.raises(ConfigError):
        load_config(path)


def test_nonexistent_file_raises() -> None:
    with pytest.raises(ConfigError):
        load_config("this_file_does_not_exist.txt")


def test_entry_not_on_border_raises(tmp_path: object) -> None:
    path = write_config(tmp_path, """
WIDTH=10
HEIGHT=10
ENTRY=5,5
EXIT=9,9
OUTPUT_FILE=maze.txt
PERFECT=True
""")
    with pytest.raises(ConfigError, match="border"):
        load_config(path)


def test_seed_not_int_raises(tmp_path: object) -> None:
    path = write_config(tmp_path, """
WIDTH=10
HEIGHT=10
ENTRY=0,0
EXIT=9,9
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=abc
""")
    with pytest.raises(ConfigError):
        load_config(path)
