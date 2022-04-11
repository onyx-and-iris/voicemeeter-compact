import toml
from pathlib import Path

configuration = {}

config_path = [Path.cwd() / "configs"]
for path in config_path:
    if path.is_dir():
        filenames = list(path.glob("*.toml"))
        configs = {}
        for filename in filenames:
            name = filename.with_suffix("").stem
            try:
                configs[name] = toml.load(filename)
            except toml.TomlDecodeError:
                print(f"Invalid TOML profile: configs/{filename.stem}")

        for name, cfg in configs.items():
            print(f"Loaded profile configs/{name}")
            configuration[name] = cfg
