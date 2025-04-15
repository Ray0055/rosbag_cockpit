"""
ROS Bag player for the Cockpit application.

This module provides functionality to play ROS bag files.
"""

import os
import subprocess
import threading
import time
from typing import Any, Dict, List, Optional

from .error import BagPlaybackBusyError


class RosbagPlayer:
    """Player for ROS bag files."""

    def __init__(self):
        """Initialize the ROS bag player."""

        self.bag_lock = threading.Lock()
        self.bag_process = None

        self.stop_playback_event = (
            threading.Event()
        )  # a threading event to signal when to stop playback
        self.playback_thread = None

    def play_bag(
        self,
        bag_path: str,
        topics: Optional[List[str]] = None,
        loop: bool = False,
        clock: bool = True,
    ) -> bool:
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

        cmd = ["ros2", "bag", "play", bag_path]

        if loop:
            cmd.append("--loop")

        if clock:
            cmd.append("--clock")

        if topics:
            cmd.append("--topics")
            cmd.extend(topics)

        # Create a shell command with source commands and the ros2 bag play command
        shell_cmd = (
            "source /opt/ros/galactic/setup.bash &&"
            "source /home/driverless/workspace/install/setup.bash && " + " ".join(cmd)
        )

        with self.bag_lock:
            if self.playback_thread and self.playback_thread.is_alive():
                raise BagPlaybackBusyError()

            self.stop_playback_event.clear()  # Clear the stop playback event

            # Start the playback in a separate thread
            self.playback_thread = threading.Thread(
                target=self._play_bag_thread,
                args=(shell_cmd,),
                daemon=True,
            )
            self.playback_thread.start()
            time.sleep(0.1)

            return self.playback_thread.is_alive()

    def _play_bag_thread(self, shell_cmd: str) -> None:
        """
        Thread target for playing the bag file.

        Args:
            shell_cmd: Shell command to execute
        """
        try:
            with self.bag_lock:
                self.bag_process = subprocess.Popen(
                    ["bash", "-c", shell_cmd],
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

            print("Bag playback started")

            # Wait for the process to finish or until the stop event is set
            while not self.stop_playback_event.is_set() or self.bag_process.poll() is None:
                time.sleep(0.1)  # Sleep for a short duration to avoid busy waiting

            # if process is still running, but stop_playback is set, terminate the process
            if self.bag_process.poll() is None and self.stop_playback_event.is_set():
                with self.bag_lock:
                    self.bag_process.terminate()
                    self.bag_process.wait(timeout=2.0)
                    print("Bag playback stopped")
            print("Bag playback finished")
        except Exception as e:
            print(f"Error during bag playback: {e}")
        finally:
            with self.bag_lock:
                self.bag_process = None

    def stop_playback(self) -> str:
        """
        Stop a running bag playback process.

        Args:
            process: Subprocess object representing the rosbag play process
        """
        self.stop_playback_event.set()  # Set the stop playback event
        with self.bag_lock:
            if self.bag_process and self.bag_process.poll() is None:
                try:
                    self.bag_process.terminate()
                    self.bag_process.wait(timeout=2.0)
                    print("Bag playback stopped")
                    return "Bag playback stopped"
                except Exception as e:
                    print(f"Error stopping bag playback: {e}")
            else:
                print("No bag is currently being played")
                return "No bag is currently being played"

    def get_playback_status(self) -> Dict[str, Any]:
        """
        Get the status of a running bag playback process.

        Args:
            process: Subprocess object representing the rosbag play process

        Returns:
            Dictionary containing status information
        """

        with self.bag_lock:
            playback_thread = self.playback_thread and self.playback_thread.is_alive()
            process_is_running = self.bag_process and self.bag_process.poll() is None

            status = {
                "running": process_is_running and playback_thread,
                "thread_alive": playback_thread,
            }
            return status
