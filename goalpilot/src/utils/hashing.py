"""Hashing utilities for data versioning"""
import hashlib
import json
from typing import Any, Union

def compute_sha256(data: Union[str, bytes, dict]) -> str:
    """
    Compute SHA256 hash of data.
    
    Args:
        data: String, bytes, or dict to hash
        
    Returns:
        Hex string of SHA256 hash
    """
    if isinstance(data, dict):
        # Sort keys for consistent hashing
        data = json.dumps(data, sort_keys=True)
    
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    return hashlib.sha256(data).hexdigest()

def compute_file_hash(filepath: str) -> str:
    """
    Compute SHA256 hash of a file.
    
    Args:
        filepath: Path to file
        
    Returns:
        Hex string of SHA256 hash
    """
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read in chunks to handle large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

__all__ = ["compute_sha256", "compute_file_hash"]
