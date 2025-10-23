from pathlib import Path
import tomllib
from typing import Any, Final

Config = dict[str, Any] # pyright: ignore[reportExplicitAny]
Headers = dict[str, str]

def init_config(config_path: Path) -> Config:
    config: Final[Config];

    with open(config_path, "r+b") as config_bytes:
        config = tomllib.load(config_bytes)

    return config
