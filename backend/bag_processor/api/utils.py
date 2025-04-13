"""
Utility functions for the API routes.
These functions provide common functionality used across the API.
"""

import os
from pathlib import Path
from typing import Any, Dict

import yaml
from fastapi import HTTPException

# from cockpit.database.operations import get_rosbag_by_id
# from cockpit.rosbag.parser import get_rosbag_info


def load_config() -> Dict[str, Any]:
    """
    Load configuration from the YAML file.

    Returns:
        Dict[str, Any]: The configuration dictionary
    """
    config_path = os.environ.get("COCKPIT_CONFIG", "config/default.yaml")
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except Exception:
        # Fallback to default config if file not found or invalid
        return {
            "database": {"url": "sqlite:///cockpit.db"},
            "api": {"host": "0.0.0.0", "port": 8000},
            "rosbag": {"storage_dir": "data/rosbags"},
        }


def validate_rosbag_path(path: str) -> Path:
    """
    Validate that a rosbag file exists at the given path.

    Args:
        path (str): Path to the rosbag file

    Returns:
        Path: Validated Path object

    Raises:
        HTTPException: If the rosbag file does not exist
    """
    p = Path(path)
    if not p.exists():
        raise HTTPException(status_code=404, detail=f"Rosbag file not found at {path}")
    if not p.is_file():
        raise HTTPException(status_code=400, detail=f"Path {path} is not a file")
    if not str(p).endswith(".bag"):
        raise HTTPException(status_code=400, detail=f"File {path} is not a rosbag file")
    return p


# def get_rosbag_or_404(db: Session, rosbag_id: int):
#     """
#     Get a rosbag by ID or raise a 404 error.

#     Args:
#         db (Session): Database session
#         rosbag_id (int): ID of the rosbag

#     Returns:
#         Rosbag: The rosbag object

#     Raises:
#         HTTPException: If the rosbag is not found
#     """
#     rosbag = get_rosbag_by_id(db, rosbag_id)
#     if rosbag is None:
#         raise HTTPException(
#             status_code=404, detail=f"Rosbag with ID {rosbag_id} not found"
#         )
#     return rosbag


# def analyze_rosbag_file(path: str) -> Dict[str, Any]:
#     """
#     Analyze a rosbag file and extract metadata.

#     Args:
#         path (str): Path to the rosbag file

#     Returns:
#         Dict[str, Any]: Metadata about the rosbag

#     Raises:
#         HTTPException: If there is an error analyzing the rosbag
#     """
#     try:
#         return get_rosbag_info(path)
#     except Exception as e:
#    raise HTTPException(status_code=500, detail=f"Error analyzing rosbag: {str(e)}")


def format_size(size_bytes: int) -> str:
    """
    Format a size in bytes to a human-readable string.

    Args:
        size_bytes (int): Size in bytes

    Returns:
        str: Human-readable size string
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def format_duration(seconds: float) -> str:
    """
    Format a duration in seconds to a human-readable string.

    Args:
        seconds (float): Duration in seconds

    Returns:
        str: Human-readable duration string
    """
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m {seconds:.2f}s"
    elif minutes > 0:
        return f"{int(minutes)}m {seconds:.2f}s"
    else:
        return f"{seconds:.2f}s"
