from __future__ import annotations
import sys
from typing import Any
import random

class ConfigError(Exception):
    """Raised when the configuration file is invalid or missing."""


def load_config(path: str) -> dict[str, Any]:
    """Load and validate a maze configuration file.

    Parses a plain-text file with KEY=VALUE pairs, validates all required
    keys, converts types, and returns a fully resolved config dictionary.

    Args:
        path: Filesystem path to the configuration file.

    Returns:
        A dictionary with validated config values (WIDTH, HEIGHT, ENTRY,
        EXIT, OUTPUT_FILE, PERFECT, and optionally SEED).

    Raises:
        ConfigError: If the file is missing, has invalid syntax, or any
            value violates the constraints (out of bounds, missing keys,
            etc.).
    """
    required_keys: set[str] = {
        "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"
    }
    try:
        with open(path, "r") as f:
            config_dict: dict[str, Any] = {}
            for line in f:
                line = line.strip()
                if line == "":
                    continue
                if line.startswith("#"):
                    continue
                key, value = line.split("=")
                config_dict[key] = value
    except FileNotFoundError as e:
        raise ConfigError(f"Invalid path file: {e}")
    if not required_keys.issubset(config_dict.keys()):
        missing = required_keys - config_dict.keys()
        raise ConfigError(f"Erro: Missing parameters or not well formated: "
                          f"{missing}")
    try:
        config_dict["WIDTH"] = int(config_dict["WIDTH"])
        config_dict["HEIGHT"] = int(config_dict["HEIGHT"])
        a, b = config_dict["ENTRY"].split(",")
        config_dict["ENTRY"] = (int(a), int(b))
        c, d = config_dict["EXIT"].split(",")
        config_dict["EXIT"] = (int(c), int(d))
        config_dict["OUTPUT_FILE"] = str(config_dict["OUTPUT_FILE"])
        if "SEED" in config_dict:
            config_dict["SEED"] = int(config_dict["SEED"])
    except (IndexError, ValueError) as e:
        raise ConfigError(f"Error: {e}")
    if "SEED" not in config_dict:
        config_dict["SEED"] = random.randint(1, 1000)
    if config_dict["ENTRY"] == config_dict["EXIT"]:
        raise ConfigError("Entry and exit should be in diferent places")
    if config_dict["WIDTH"] <= 0:
        raise ConfigError("Width should be bigger than 0")
    if config_dict["HEIGHT"] <= 0:
        raise ConfigError("Height should be bigger than 0")
    for name, (ex, ey) in [("Entry", config_dict["ENTRY"]),
                           ("Exit", config_dict["EXIT"])]:
        if ex < 0 or ex >= config_dict["WIDTH"]:
            raise ConfigError(f"{name} should be inside the maze x and y")
        if ey < 0 or ey >= config_dict["HEIGHT"]:
            raise ConfigError(f"{name} should be inside the maze x and y")
        if (ex != 0 and ex != config_dict["WIDTH"] - 1
                and ey != 0 and ey != config_dict["HEIGHT"] - 1):
            raise ConfigError(f"{name} must be on the maze border")
    if (config_dict["PERFECT"] != "True" and
            config_dict["PERFECT"] != "False"):
        raise ConfigError('Perfect should be formated as: "True"/"False"')
    if config_dict["PERFECT"] == "True":
        config_dict["PERFECT"] = True
    else:
        config_dict["PERFECT"] = False
    if "SEED" in config_dict:
        config_dict["SEED"] = int(config_dict["SEED"])
    else:
        config_dict["SEED"] = 42
    return config_dict


if __name__ == "__main__":
    path = sys.argv[1]
    resultado = load_config(path)
    print(resultado)
