import logging
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

logger = logging.getLogger(__name__)

configuration = {}

configpaths = [
    Path.cwd() / "configs",
    Path.home() / ".config" / "vm-compact" / "configs",
    Path.home() / "Documents" / "Voicemeeter" / "configs",
]
for configpath in configpaths:
    if configpath.is_dir():
        filepaths = list(configpath.glob("*.toml"))
        if any(f.stem in ("app", "vban") for f in filepaths):
            configs = {}
            for filepath in filepaths:
                filename = filepath.with_suffix("").stem
                if filename in ("app", "vban"):
                    try:
                        with open(filepath, "rb") as f:
                            configs[filename] = tomllib.load(f)
                        logger.info(f"{filename} loaded into memory")
                    except tomllib.TOMLDecodeError:
                        logger.error(f"Invalid TOML config: configs/{filename.stem}")

            configuration |= configs
            break

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
