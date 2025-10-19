"""File I/O utilities"""
import json
from pathlib import Path
from typing import Any, Dict

def read_json(filepath: str) -> Dict[str, Any]:
    """Read JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def write_json(data: Dict[str, Any], filepath: str, indent: int = 2) -> None:
    """Write JSON file"""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=indent)

__all__ = ["read_json", "write_json"]
