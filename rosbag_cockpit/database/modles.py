"""
Database models for the Cockpit application.

This module defines the SQLite table structures as Python classes.
"""

import json
from datetime import datetime
from typing import Any, Dict, List


class RosbagMetadata:
    """Represents a ROS bag metadata entry in the database."""

    def __init__(
        self,
        file_path: str,
        map_category: str,
        start_time: datetime,
        end_time: datetime,
        duration: float,
        size_mb: float,
        message_count: int,
        topic_count: int,
        topics_json: str,
        metadata_json: str,
        **additional_fields: Any,
    ):
        """
        Initialize a RosbagMetadata object.

        Args:
            file_path: Path to the ROS bag file
            map_category: Category of map (skidpad, acceleration, autox, track_driver)
            start_time: Start timestamp of the recording
            end_time: End timestamp of the recording
            duration: Duration in seconds
            size_mb: File size in megabytes
            message_count: Total number of messages
            topic_count: Number of topics
            topics_json: JSON array of topic names
            metadata_json: Additional metadata in JSON format
            additional_fields: Any additional metadata fields discovered in the bag
        """
        self.file_path = file_path
        self.map_category = map_category
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.size_mb = size_mb
        self.message_count = message_count
        self.topic_count = topic_count
        self.topics_json = topics_json
        self.metadata_json = metadata_json

        # Add any additional fields
        for key, value in additional_fields.items():
            setattr(self, key, value)

    @property
    def topics(self) -> List[str]:
        """Get the list of topics from the JSON string."""
        return json.loads(self.topics_json)

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the additional metadata as a dictionary."""
        return json.loads(self.metadata_json)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the object to a dictionary for database insertion."""
        result = {
            "file_path": self.file_path,
            "map_category": self.map_category,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "size_mb": self.size_mb,
            "message_count": self.message_count,
            "topic_count": self.topic_count,
            "topics_json": self.topics_json,
            "metadata_json": self.metadata_json,
        }

        # Add any additional attributes
        for attr in dir(self):
            if (
                not attr.startswith("_")
                and attr not in result
                and attr not in ["topics", "metadata", "to_dict"]
            ):
                result[attr] = getattr(self, attr)

        return result


class SchemaModification:
    """Represents a schema modification entry in the database."""

    def __init__(self, column_name: str, data_type: str):
        """
        Initialize a SchemaModification object.

        Args:
            column_name: Name of the column
            data_type: SQLite data type for the column
        """
        self.column_name = column_name
        self.data_type = data_type
