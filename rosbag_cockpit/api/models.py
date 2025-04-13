"""
API data models for request and response validation.
These Pydantic models define the structure of data exchanged through the API.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


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


class Rosbag(RosbagBase):
    """Full rosbag model including database fields."""

    id: int = Field(..., description="Unique ID of the rosbag entry")
    path: str = Field(..., description="Path to the rosbag file")
    size_bytes: Optional[int] = Field(None, description="Size of the rosbag file in bytes")
    duration_seconds: Optional[float] = Field(None, description="Duration of the rosbag in seconds")
    start_time: Optional[datetime] = Field(None, description="Start time of the rosbag recording")
    end_time: Optional[datetime] = Field(None, description="End time of the rosbag recording")
    topic_count: Optional[int] = Field(None, description="Number of topics in the rosbag")
    message_count: Optional[int] = Field(None, description="Number of messages in the rosbag")
    tags: List[str] = Field(default=[], description="List of tags for the rosbag")
    created_at: datetime = Field(..., description="Time when the entry was created")
    updated_at: Optional[datetime] = Field(None, description="Time when the entry was last updated")

    class Config:
        orm_mode = True


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
