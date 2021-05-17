from os import path
from pathlib import Path


def get_resources_path() -> Path:
    current_path = Path(path.dirname(path.realpath(__file__)))
    return current_path / ".." / ".." / "resources" / "pse_data"
