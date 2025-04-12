"""
ROS Bag utility functions for the Cockpit application.

This module provides utility functions for working with ROS bag files.
"""

from pathlib import Path
from typing import List


# Map categories recognized by the application
MAP_CATEGORIES = ["skidpad", "acceleration", "autox", "track_driver"]


def determine_map_category(bag_path: str) -> str:
    """
    Determine the map category based on the bag file path.
    
    Args:
        bag_path: Path to the ROS bag file
        
    Returns:
        Map category string ("skidpad", "acceleration", "autox", "track_driver", or "unknown")
    """
    path = Path(bag_path)
    for category in MAP_CATEGORIES:
        if category in str(path):
            return category
    return "unknown"


def sanitize_topic_name(topic_name: str) -> str:
    """
    Convert a ROS topic name to a valid SQLite column name.
    
    Args:
        topic_name: ROS topic name
        
    Returns:
        Sanitized column name string
    """
    # Replace slashes, spaces and special characters with underscores
    sanitized = topic_name.replace('/', '_').replace(' ', '_')
    sanitized = ''.join(c if c.isalnum() or c == '_' else '_' for c in sanitized)
    
    # Ensure it doesn't start with a number
    if sanitized and sanitized[0].isdigit():
        sanitized = f"t_{sanitized}"
        
    return sanitized


def get_rosbag_topics(bag_path: str) -> List[str]:
    """
    Get a list of topics in a ROS bag file without loading the whole file.
    
    Args:
        bag_path: Path to the ROS bag file
        
    Returns:
        List of topic names
    """
    import bag_manager
    try:
        bag = bag_manager.Bag(bag_path)
        info = bag.get_type_and_topic_info()
        topics = list(info.topics.keys())
        bag.close()
        return topics
    except Exception as e:
        print(f"Error reading topics from {bag_path}: {str(e)}")
        return []


def format_duration(seconds: float) -> str:
    """
    Format a duration in seconds to a human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string (e.g., "1h 23m 45s")
    """
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def human_readable_size(size_bytes: int) -> str:
    """
    Convert file size in bytes to a human-readable string.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Human-readable size string (e.g., "1.23 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0 or unit == 'TB':
            break
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} {unit}"