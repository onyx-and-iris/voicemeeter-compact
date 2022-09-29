import logging
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

LOGGER = logging.getLogger("configurations")

configuration = {}

config_path = [Path.cwd() / "configs"]
for path in config_path:
    if path.is_dir():
        filenames = list(path.glob("*.toml"))
        configs = {}
        for filename in filenames:
            name = filename.with_suffix("").stem
            try:
                with open(filename, "rb") as f:
                    configs[name] = tomllib.load(f)
            except tomllib.TOMLDecodeError:
                print(f"Invalid TOML config: configs/{filename.stem}")

        for name, cfg in configs.items():
            LOGGER.info(f"Loaded configuration configs/{name}")
            configuration[name] = cfg

_defaults = {
    "configs": {
        "config": None,
    },
    "theme": {
        "enabled": True,
        "mode": "light",
    },
    "extends": {
        "extended": True,
        "extends_horizontal": True,
    },
    "channel": {
        "width": 80,
        "height": 130,
    },
    "mwscroll_step": {
        "size": 3,
    },
    "submixes": {
        "default": 0,
    },
}

if "app" in configuration:
    configuration["app"] = _defaults | configuration["app"]
else:
    configuration["app"] = _defaults


def get_configuration(key):
    if key in configuration:
        return configuration[key]
