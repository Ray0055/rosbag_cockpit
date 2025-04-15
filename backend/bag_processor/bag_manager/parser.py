"""
ROS Bag parser for the Cockpit application.

This module provides functionality to parse ROS bag files and extract metadata.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import yaml

from ..database import RosbagMetadata
from .utils import sanitize_topic_name

# import rosbag


class RosbagParser:
    """Parser for ROS bag files."""

    def __init__(self):
        """Initialize the ROS bag parser."""
        pass

    def parse_bag_folder(self, bag_folder_path: str) -> Optional[RosbagMetadata]:
        """
        Parse a ROS bag file and extract metadata.

        Args:
            bag_path: Path to the ROS bag file

        Returns:
            RosbagMetadata object containing the extracted metadata,
            or None if parsing failed
        """
        if not os.path.exists(bag_folder_path):
            print(f"Error: Bag file does not exist: {bag_folder_path}")
            return None

        try:
            return self._extract_bag_metadata(bag_folder_path)
        except Exception as e:
            print(f"Error processing bag file {bag_folder_path}: {str(e)}")
            return None

    def _extract_bag_metadata(self, bag_folder_path: str) -> RosbagMetadata:
        """
        Extract metadata from a ROS bag file. Input bag_path is validated.

        Args:
            bag_path: Path to the ROS bag file.

        Returns:
            RosbagMetadata object containing the extracted metadata
        """
        mcap_files = [f for f in os.listdir(bag_folder_path) if f.endswith(".mcap")]
        db3_files = [f for f in os.listdir(bag_folder_path) if f.endswith(".db3")]

        if len(mcap_files) + len(db3_files) > 1:
            raise ValueError(f"Multiple bag files found in directory: {bag_folder_path}")
        elif len(mcap_files) + len(db3_files) == 0:
            raise ValueError(f"No bag files found in directory: {bag_folder_path}")
        else:
            bag_path = os.path.join(bag_folder_path, mcap_files[0] if mcap_files else db3_files[0])
            file_size = os.path.getsize(bag_path) / (1024 * 1024)  # Convert to MB

            if len(mcap_files) == 1:
                if os.path.exists(bag_folder_path + "/metadata.yaml"):
                    metadata = self._extract_bag_metadata_from_yaml(bag_folder_path)
                    metadata.file_path = os.path.join(bag_folder_path, mcap_files[0])
                    metadata.file_type = "mcap"
                    metadata.file_name = mcap_files[0]
                    metadata.size_mb = file_size
                    return metadata

                else:
                    return self._extract_bag_metadata_from_mcap(
                        os.path.join(bag_folder_path, mcap_files[0])
                    )

            elif len(db3_files) == 1:
                if os.path.exists(bag_folder_path + "/metadata.yaml"):
                    metadata = self._extract_bag_metadata_from_yaml(bag_folder_path)
                    metadata.file_path = os.path.join(bag_folder_path, db3_files[0])
                    metadata.file_type = "db3"
                    metadata.file_name = db3_files[0]
                    metadata.size_mb = file_size
                    return metadata

                else:
                    return self._extract_bag_metadata_from_rosbag(
                        os.path.join(bag_folder_path, db3_files[0])
                    )
            else:
                raise ValueError(f"Unsupported bag file format in directory: {bag_folder_path}")

    def _extract_bag_metadata_from_yaml(self, bag_path: str) -> RosbagMetadata:
        """
        Extract metadata from a ROS bag file using YAML.
        Bag_path is validated.

        Args:
            bag_path: Path to the ROS bag file

        Returns:
            RosbagMetadata object containing the extracted metadata
        """
        with open(bag_path + "/metadata.yaml", "r") as f:
            metadata = yaml.safe_load(f)
            metadata = self._convert_metaData_toRosbagMetadata(metadata, bag_path)
            print(f"Converted matadata from yaml: {bag_path + '/metadata.yaml'}")
            return metadata

    def _convert_metaData_toRosbagMetadata(
        self, metadata: Dict[str, Any], bag_folder_path: str = ""
    ) -> RosbagMetadata:
        """
        Convert metadata dictionary to RosbagMetadata object.

        Args:
            metadata: Dictionary containing metadata

        Returns:
            RosbagMetadata object
        """

        # Create and return the metadata object
        # 获取基础字段
        metadata = metadata["rosbag2_bagfile_information"]
        duration_ns = metadata["duration"]["nanoseconds"]
        duration_sec = duration_ns / 1e9  # 转换为秒

        start_time_ns = metadata["starting_time"]["nanoseconds_since_epoch"]
        # 转换为datetime对象 (Unix时间戳从1970年开始计算)
        start_time = datetime.fromtimestamp(start_time_ns / 1e9).strftime("%Y-%m-%d-%H-%M-%S")

        # 计算结束时间
        end_time = datetime.fromtimestamp((start_time_ns + duration_ns) / 1e9).strftime(
            "%Y-%m-%d-%H-%M-%S"
        )

        message_count = metadata["message_count"]

        # 获取所有主题
        topics = [topic["topic_metadata"] for topic in metadata["topics_with_message_count"]]
        for i, topic_with_count in enumerate(metadata["topics_with_message_count"]):
            # 将 message_count 直接添加到对应的 topic 字典中
            topics[i]["message_count"] = topic_with_count["message_count"]
        topics_json = json.dumps(topics)

        #  Extract topic-specific counts and other metadata
        additional_metadata = {}
        for topic in topics:
            topic_key = f"topic_{sanitize_topic_name(topic['name'])}_count"
            additional_metadata[topic_key] = topic["message_count"]

        # Look for custom metadata in specific message types
        # This is where you would implement logic to extract specific data from messages

        # 创建RosbagMetadata对象
        rosbag_metadata = RosbagMetadata(
            file_path=bag_folder_path,
            file_name="",
            file_type="",
            map_category="",
            start_time=start_time,
            end_time=end_time,
            duration=duration_sec,
            size_mb=None,
            message_count=message_count,
            topic_count=len(topics),
            topics_json=topics_json,
            metadata_json=json.dumps(additional_metadata),
        )

        return rosbag_metadata

    def _extract_bag_metadata_from_mcap(self, bag_path: str) -> RosbagMetadata:
        """
        Extract metadata from a ROS bag file using MCAP.

        Args:
            bag_path: Path to the ROS bag file

        Returns:
            RosbagMetadata object containing the extracted metadata
        """
        # Placeholder for MCAP extraction logic
        pass

    def _extract_bag_metadata_from_rosbag(self, bag_path: str) -> RosbagMetadata:
        """
        Extract metadata from a ROS bag file.

        Args:
            bag_path: Path to the ROS bag file

        Returns:
            RosbagMetadata object containing the extracted metadata
        """
        # bag = rosbag.Bag(bag_path)
        # info = bag.get_type_and_topic_info()

        # # Get basic info
        # file_size = os.path.getsize(bag_path) / (1024 * 1024)  # Convert to MB

        # # Extract topic-specific counts and other metadata
        # additional_metadata = {}
        # for topic_name, topic_info in info.topics.items():
        #     topic_key = f"topic_{sanitize_topic_name(topic_name)}_count"
        #     additional_metadata[topic_key] = topic_info.message_count

        # # Look for custom metadata in specific message types
        # # This is where you would implement logic to extract specific data from
        # messages

        # # Create and return the metadata object
        # metadata = RosbagMetadata(
        #     file_path=bag_path,
        #     map_category=determine_map_category(bag_path),
        #     start_time=datetime.fromtimestamp(bag.get_start_time()),
        #     end_time=datetime.fromtimestamp(bag.get_end_time()),
        #     duration=bag.get_end_time() - bag.get_start_time(),
        #     size_mb=file_size,
        #     message_count=bag.get_message_count(),
        #     topic_count=len(info.topics),
        #     topics_json=json.dumps(list(info.topics.keys())),
        #     metadata_json=json.dumps(additional_metadata),
        # )

        # bag.close()
        # return metadata
        pass

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

        # check the directory structure is correct
        subdirectories = [
            "skidpad",
            "trackdrive",
            "autox",
            "acceleration",
            "undefined",
        ]
        for subdir in subdirectories:
            if not os.path.exists(os.path.join(directory_path, subdir)):
                raise ValueError(
                    f"Directory structure is incorrect, expected: {directory_path}/{subdir}"
                )

        result = []
        for subdir in subdirectories:
            map_category = subdir

            for root, dirs, files in os.walk(directory_path + "/" + subdir):
                for file in files:
                    if file.endswith(".db3") or file.endswith(".mcap"):
                        metadata = self.parse_bag_folder(root)
                        if metadata:
                            metadata.map_category = map_category
                            result.append(metadata)
                        break

            # subdir_path = os.path.join(directory_path, subdir)
            # res = next(os.walk(subdir_path))
            # _, dirs, files = res
            # for dir in dirs:
            #     metadata = self.parse_bag_folder(os.path.join(subdir_path, dir))
            #     if metadata:
            #         result.append(metadata)

        return result
