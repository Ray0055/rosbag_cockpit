"""
ROS Bag parser for the Cockpit application.

This module provides functionality to parse ROS bag files and extract metadata.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
# import rosbag
from pathlib import Path

from ..database import RosbagMetadata
from .utils import determine_map_category, sanitize_topic_name


class RosbagParser:
    """Parser for ROS bag files."""
    
    def __init__(self):
        """Initialize the ROS bag parser."""
        pass
    
    def parse_bag_file(self, bag_path: str) -> Optional[RosbagMetadata]:
        """
        Parse a ROS bag file and extract metadata.
        
        Args:
            bag_path: Path to the ROS bag file
            
        Returns:
            RosbagMetadata object containing the extracted metadata, or None if parsing failed
        """
        if not os.path.exists(bag_path):
            print(f"Error: Bag file does not exist: {bag_path}")
            return None
            
        try:
            return self._extract_bag_metadata(bag_path)
        except Exception as e:
            print(f"Error processing bag file {bag_path}: {str(e)}")
            return None
    
    # def _extract_bag_metadata(self, bag_path: str) -> RosbagMetadata:
    #     """
    #     Extract metadata from a ROS bag file.
        
    #     Args:
    #         bag_path: Path to the ROS bag file
            
    #     Returns:
    #         RosbagMetadata object containing the extracted metadata
    #     """
    #     bag = rosbag.Bag(bag_path)
    #     info = bag.get_type_and_topic_info()
        
    #     # Get basic info
    #     file_size = os.path.getsize(bag_path) / (1024 * 1024)  # Convert to MB
        
    #     # Extract topic-specific counts and other metadata
    #     additional_metadata = {}
    #     for topic_name, topic_info in info.topics.items():
    #         topic_key = f"topic_{sanitize_topic_name(topic_name)}_count"
    #         additional_metadata[topic_key] = topic_info.message_count
        
    #     # Look for custom metadata in specific message types
    #     # This is where you would implement logic to extract specific data from messages
        
    #     # Create and return the metadata object
    #     metadata = RosbagMetadata(
    #         file_path=bag_path,
    #         map_category=determine_map_category(bag_path),
    #         start_time=datetime.fromtimestamp(bag.get_start_time()),
    #         end_time=datetime.fromtimestamp(bag.get_end_time()),
    #         duration=bag.get_end_time() - bag.get_start_time(),
    #         size_mb=file_size,
    #         message_count=bag.get_message_count(),
    #         topic_count=len(info.topics),
    #         topics_json=json.dumps(list(info.topics.keys())),
    #         metadata_json=json.dumps(additional_metadata)
    #     )
        
    #     bag.close()
    #     return metadata
    
    def scan_directory(self, directory_path: str, recursive: bool = True) -> List[RosbagMetadata]:
        """
        Scan a directory for ROS bag files and parse them.
        
        Args:
            directory_path: Path to the directory containing ROS bag files
            recursive: Whether to search recursively through subdirectories
            
        Returns:
            List of RosbagMetadata objects for the found bag files
        """
        if not os.path.isdir(directory_path):
            print(f"Error: Directory does not exist: {directory_path}")
            return []
            
        result = []
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.bag'):
                    bag_path = os.path.join(root, file)
                    metadata = self.parse_bag_file(bag_path)
                    if metadata:
                        result.append(metadata)
                    
            if not recursive:
                break
                
        return result