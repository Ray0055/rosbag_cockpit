"""
ROS Bag processing package for the Cockpit application.

This package contains modules for parsing, playing, and analyzing ROS bag files.
"""

from .parser import RosbagParser
from .player import RosbagPlayer
from .utils import determine_map_category, sanitize_topic_name

__all__ = [
    "RosbagParser",
    "RosbagPlayer",
    "determine_map_category",
    "sanitize_topic_name",
]
