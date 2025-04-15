"""
API data models for request and response validation.
These Pydantic models define the structure of data exchanged through the API.
"""

import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class RosbagBase(BaseModel):
    """Base model for rosbag data."""

    name: str = Field(..., description="Name of the rosbag file")
    description: Optional[str] = Field(None, description="Description of the rosbag file")


class RosbagCreate(RosbagBase):
    """Model for creating a new rosbag entry."""

    path: str = Field(..., description="Path to the rosbag file")
    tags: Optional[List[str]] = Field(default=[], description="List of tags for the rosbag")


class RosbagUpdate(BaseModel):
    """Model for updating an existing rosbag entry."""

    name: Optional[str] = Field(None, description="Updated name of the rosbag file")
    description: Optional[str] = Field(None, description="Updated description of the rosbag")
    path: Optional[str] = Field(None, description="Updated path to the rosbag file")
    tags: Optional[List[str]] = Field(None, description="Updated list of tags for the rosbag")


class Topic(BaseModel):
    """Model for topic information."""

    id: int = Field(..., description="Unique ID of the topic")
    rosbag_id: int = Field(..., description="ID of the rosbag containing this topic")
    name: str = Field(..., description="Name of the topic")
    message_type: str = Field(..., description="Message type of the topic")
    message_count: int = Field(..., description="Number of messages for this topic")
    frequency: Optional[float] = Field(None, description="Publishing frequency of the topic")

    class Config:
        orm_mode = True


class Rosbag(BaseModel):
    """Model for rosbag record matching the database schema."""

    id: Optional[int] = Field(None, description="Unique ID of the rosbag")
    file_path: str = Field(..., description="Path to the rosbag file")
    file_name: Optional[str] = Field(None, description="Name of the rosbag file")
    file_type: Optional[str] = Field(None, description="Type of the file (e.g., .bag, .mcap)")
    map_category: Optional[str] = Field(None, description="Category of the map")
    start_time: Optional[str] = Field(None, description="Start time of the recording")
    end_time: Optional[str] = Field(None, description="End time of the recording")
    duration: Optional[float] = Field(None, description="Duration of the recording in seconds")
    size_mb: Optional[float] = Field(None, description="Size of the file in MB")
    message_count: Optional[int] = Field(None, description="Total number of messages")
    topic_count: Optional[int] = Field(None, description="Number of topics")
    topics: Optional[List[Topic]] = Field(None, description="List of topics in the rosbag")
    metadata: Optional[Dict] = Field(None, description="Additional metadata")
    created_at: Optional[str] = Field(None, description="Creation timestamp")

    # Add a field to store topic count data
    topic_counts: Dict[str, Optional[int]] = Field(
        default_factory=dict, description="Topic message counts"
    )

    model_config = {"extra": "ignore"}  # Allow extra fields to be set during initialization

    @model_validator(mode="before")
    @classmethod
    def extract_topic_counts(cls, data: Dict) -> Dict:
        if not isinstance(data, dict):
            return data

        # Process any fields that match the pattern "topic__*_count"
        topic_counts = {}
        for key, value in list(data.items()):
            if key.startswith("topic__") and key.endswith("_count"):
                # Extract the topic name (remove "topic__" and "_count")
                topic_name = key[7:-6]  # Remove "topic__" and "_count"
                # Replace underscore with slash for the actual topic name
                topic_name = "/" + topic_name.replace("_", "/")
                topic_counts[topic_name] = value

        # Add the extracted counts to the data
        data["topic_counts"] = topic_counts
        return data

    @field_validator("topics", mode="before")
    @classmethod
    def parse_topics_json(cls, v, info):
        if v is not None:
            return v

        values = info.data
        topics_json = values.get("topics_json")
        if topics_json:
            try:
                return json.loads(topics_json)
            except json.JSONDecodeError:
                pass
        return None

    @field_validator("metadata", mode="before")
    @classmethod
    def parse_metadata_json(cls, v, info):
        if v is not None:
            return v

        values = info.data
        metadata_json = values.get("metadata_json")
        if metadata_json:
            try:
                return json.loads(metadata_json)
            except json.JSONDecodeError:
                pass
        return None


class TopicCreate(BaseModel):
    """Model for creating a new topic."""

    rosbag_id: int
    name: str
    message_type: str
    message_count: int
    frequency: Optional[float] = None


class MessageQuery(BaseModel):
    """Model for querying messages from a rosbag."""

    topic_names: List[str] = Field(..., description="List of topic names to query")
    start_time: Optional[float] = Field(None, description="Start time in seconds")
    end_time: Optional[float] = Field(None, description="End time in seconds")
    limit: Optional[int] = Field(100, description="Maximum number of messages to return")
    offset: Optional[int] = Field(0, description="Number of messages to skip")


class Message(BaseModel):
    """Model for a message from a rosbag."""

    topic: str = Field(..., description="Name of the topic")
    timestamp: float = Field(..., description="Timestamp of the message in seconds")
    data: Dict[str, Any] = Field(..., description="Message data")


class ErrorResponse(BaseModel):
    """Model for error responses."""

    detail: str = Field(..., description="Error message")


class SuccessResponse(BaseModel):
    """Model for success responses."""

    message: str = Field(..., description="Success message")
    data: Optional[Any] = Field(None, description="Response data")


class DatabaseStats(BaseModel):
    """Model for system statistics."""

    rosbag_count: int = Field(..., description="Total number of rosbags")
    total_columns: int = Field(..., description="Total number of columns in the database")


class DockerImageInfo(BaseModel):
    id: str
    tags: List[str]
    size: int
    created: str


class DockerContainerInfo(BaseModel):
    id: str
    name: str
    image_tags: Optional[List[str]] = None
    status: str
    ports: Dict[str, Any]
    created: str
    labels: Optional[Dict[str, str]] = None
