import sys


class ConfigError(Exception):
    pass


def load_config(path):
    required_keys = {
        "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"
    }
    try:
        with open(path, "r") as f:
            config_dict = {}
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
    except (IndexError, ValueError) as e:
        raise ConfigError(f"Error: {e}")
    if config_dict["ENTRY"] == config_dict["EXIT"]:
        raise ConfigError("Entry and exit should be in diferent places")
    if config_dict["WIDTH"] <= 0:
        raise ConfigError("Width should be bigger than 0")
    if config_dict["HEIGHT"] <= 0:
        raise ConfigError("Height should be bigger than 0")
    if (config_dict["ENTRY"][0] < 0 or
            config_dict["ENTRY"][0] >= config_dict["WIDTH"]):
        raise ConfigError("Entry should be inside the maze x and y")
    if (config_dict["ENTRY"][1] < 0 or
            config_dict["ENTRY"][1] >= config_dict["HEIGHT"]):
        raise ConfigError("Entry should be inside the maze x and y")
    if (config_dict["EXIT"][0] < 0 or
            config_dict["EXIT"][0] >= config_dict["WIDTH"]):
        raise ConfigError("Exit should be inside the maze x and y")
    if (config_dict["EXIT"][1] < 0 or
            config_dict["EXIT"][1] >= config_dict["HEIGHT"]):
        raise ConfigError("Exit should be inside the maze x and y")
    if (config_dict["PERFECT"] != "True" and
            config_dict["PERFECT"] != "False"):
        raise ConfigError("Perfect should be formated as: ´True´/´False´")
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
