import logging
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

logger = logging.getLogger(__name__)

configuration = {}


def get_configpath():
    configpaths = [
        Path.cwd() / "configs",
        Path.home() / ".config" / "vm-compact" / "configs",
        Path.home() / "Documents" / "Voicemeeter" / "configs",
    ]
    for configpath in configpaths:
        if configpath.exists():
            return configpath


if configpath := get_configpath():
    filepaths = list(configpath.glob("*.toml"))
    if any(f.stem in ("app", "vban") for f in filepaths):
        configs = {}
        for filepath in filepaths:
            filename = filepath.with_suffix("").stem
            if filename in ("app", "vban"):
                try:
                    with open(filepath, "rb") as f:
                        configs[filename] = tomllib.load(f)
                    logger.info(f"configuration: {filename} loaded into memory")
                except tomllib.TOMLDecodeError:
                    logger.error(f"Invalid TOML config: configs/{filename.stem}")
        configuration |= configs

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
        "xpadding": 3,
    },
    "mwscroll_step": {
        "size": 3,
    },
    "submixes": {
        "default": 0,
    },
    "navigation": {"show": True},
}


if "app" in configuration:
    for key in _defaults:
        if key in configuration["app"]:
            configuration["app"][key] = _defaults[key] | configuration["app"][key]
        else:
            configuration["app"][key] = _defaults[key]
else:
    configuration["app"] = _defaults


def get_configuration(key):
    if key in configuration:
        return configuration[key]


def loader(kind_id, target):
    configs = {"reset": target.configs["reset"]}
    if configpath := get_configpath():
        userconfigpath = configpath / kind_id
        if userconfigpath.exists():
            filepaths = list(userconfigpath.glob("*.toml"))
            for filepath in filepaths:
                identifier = filepath.with_suffix("").stem
                try:
                    with open(filepath, "rb") as f:
                        configs[identifier] = tomllib.load(f)
                    logger.info(f"loader: {identifier} loaded into memory")
                except tomllib.TOMLDecodeError:
                    logger.error(f"Invalid TOML config: configs/{filename.stem}")

    target.configs = configs
    return target.configs
