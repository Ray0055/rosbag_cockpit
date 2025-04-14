"""
ROS Bag player for the Cockpit application.

This module provides functionality to play ROS bag files.
"""

import os
import subprocess
from typing import Any, Dict, List, Optional


class RosbagPlayer:
    """Player for ROS bag files."""

    def __init__(self):
        """Initialize the ROS bag player."""
        pass

    def play_bag(
        self,
        bag_path: str,
        topics: Optional[List[str]] = None,
        loop: bool = False,
        clock: bool = True,
    ) -> subprocess.Popen:
        """
        Play a ROS bag file using the rosbag play command.

        Args:
            bag_path: Path to the ROS bag file
            topics: List of topics to play (if None, all topics are played)
            rate: Playback rate multiplier
            start: Start time in seconds
            duration: Play duration in seconds (if None, play until the end)
            loop: Whether to loop the playback
            clock: Whether to publish the clock message

        Returns:
            Subprocess object representing the rosbag play process
        """
        if not os.path.exists(bag_path):
            raise FileNotFoundError(f"Bag file does not exist: {bag_path}")

        cmd = ["ros2","bag", "play", bag_path+f"{bag_path}_0.db3"]

        if loop:
            cmd.append("--loop")

        if clock:
            cmd.append("--clock")

        if topics:
            cmd.append("--topics")
            cmd.extend(topics)

        # Create a shell command with source commands and the ros2 bag play command
        shell_cmd = "source /opt/ros/galactic/setup.bash && source /home/driverless/workspace/install/setup.bash && " + " ".join(cmd)
        # Run the command
        process = subprocess.Popen(shell_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        print(f"Started playing bag file: {bag_path}")
        return process

    def stop_playback(self, process: subprocess.Popen) -> None:
        """
        Stop a running bag playback process.

        Args:
            process: Subprocess object representing the rosbag play process
        """
        if process.poll() is None:  # Check if the process is still running
            process.terminate()
            process.wait()
            print("Stopped bag playback")

    def get_playback_status(self, process: subprocess.Popen) -> Dict[str, Any]:
        """
        Get the status of a running bag playback process.

        Args:
            process: Subprocess object representing the rosbag play process

        Returns:
            Dictionary containing status information
        """
        status = {
            "running": process.poll() is None,
            "return_code": process.returncode if process.poll() is not None else None,
        }

        return status
