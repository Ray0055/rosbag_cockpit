import subprocess
import threading
from typing import List

from fastapi import HTTPException

from ..api.schema import Rosbag, from_dict_to_database_stats, from_dicts_to_rosbags
from ..database.operations import DatabaseManager
from .models import DockerContainerConfig, DockerContainerInfo, DockerImageInfo


class DatabaseService:
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the DatabaseService.

        Args:
            db_manager: DatabaseManager instance
        """
        self.db_manager = db_manager

    def get_database_stats(self):
        """
        Get database statistics.

        Returns:
            dict: Database statistics
        """
        res = self.db_manager.get_database_stats()
        return from_dict_to_database_stats(res)

    def get_rosbags_by_map_category(self, map_category: str):
        """
        Get all rosbag entries for a specific map category.

        Args:
            map_category: Map category to filter by

        Returns:
            List of dictionaries containing rosbag data
        """
        return self.db_manager.get_rosbags_by_map_category(map_category)

    def get_all_rosbags(self) -> List[Rosbag]:
        """
        Get all rosbag entries.

        Returns:
            List of dictionaries containing rosbag data
        """
        return from_dicts_to_rosbags(self.db_manager.get_all_rosbags())

    def get_rosbag_by_path_or_404(self, bag_path: str) -> Rosbag:
        """
        Get a rosbag by ID or raise a 404 error.

        Args:
            db (Session): Database session
            rosbag_id (int): ID of the rosbag

        Returns:
            Rosbag: The rosbag object

        Raises:
            HTTPException: If the rosbag is not found
        """
        rosbag = self.db_manager.get_rosbag_by_path(bag_path)
        if rosbag is None:
            raise HTTPException(status_code=404, detail=f"Rosbag with path {bag_path} not found")
        return from_dicts_to_rosbags([rosbag])[0]


class DockerService:
    def __init__(self, docker_client):
        """
        Initialize the DockerService.

        Args:
            docker_client: Docker client instance
        """
        self.docker_client = docker_client

    def run_container_from_image(self, image_tag: str, config: DockerContainerConfig):
        """
        Run a Docker container with the specified image tag.

        Args:
            image_tag: Docker image tag

        Returns:
            dict: Container details
        """
        try:
            container = self.docker_client.containers.run(
                image_tag,
                detach=True,
                name=config.name,
                volumes=config.volumes,
                ports=config.ports,
                environment=config.environment,
                command=config.command,
                network=config.network,
            )

            return {"status": "success", "container_id": container.id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def list_all_images(self) -> List[DockerImageInfo]:
        """
        List all Docker images.

        Returns:
            List of Docker images
        """
        try:
            image_info = []
            for image in self.docker_client.images.list():
                image_info.append(
                    DockerImageInfo(
                        id=image.id,
                        tags=image.tags,
                        created=image.attrs["Created"],
                        size=image.attrs["Size"],
                    )
                )
            return image_info
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def list_all_containers(self):
        """
        List all Docker containers.

        Returns:
            List of Docker containers
        """
        try:
            container_info = []
            for container in self.docker_client.containers.list(all=True):
                container_info.append(
                    DockerContainerInfo(
                        id=container.id,
                        name=container.name,
                        image_tags=container.image.tags,
                        status=container.status,
                        ports=container.ports,
                        created=container.attrs["Created"],
                        labels=container.labels,
                    )
                )
            return container_info
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def remove_container_by_id(self, container_id: str):
        """
        Delete a Docker container by ID.

        Args:
            container_id: Docker container ID

        Returns:
            dict: Deletion status
        """
        try:
            container = self.docker_client.containers.get(container_id)
            container.stop()
            container.remove(force=True)
            return {
                "status": "success",
                "message": f"Container {container_id} deleted successfully",
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            # TODO: thie error handling is not detailed enough

    def stop_container_by_id(self, container_id: str):
        """
        Stop a Docker container by ID.

        Args:
            container_id: Docker container ID

        Returns:
            dict: Stopping status
        """
        try:
            container = self.docker_client.containers.get(container_id)
            container.stop()
            return {
                "status": "success",
                "message": f"Container {container_id} stopped successfully",
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


class RosPublisherService:
    def __init__(self):
        """
        Initialize the PublishService.

        Args:
            rosbag_manager: RosbagManager instance
        """
        self.publish_lock = threading.Lock()
        self.publish_process = None

    def publish_masterlogic(self, as_state: str, active_mission: str):
        """
        Publish a message to a ROS topic.

        Args:
            topic: The topic to publish
            message: The message to publish

        Returns:
            dict: Publishing status
        """
        with self.publish_lock:
            if self.publish_process and self.publish_process.poll() is None:
                raise HTTPException(
                    status_code=400, detail="master logic is already being published"
                )
            else:
                master_logic_msg = [
                    "ros2",
                    "topic",
                    "pub",
                    "--rate",
                    str(1),
                    "/master_logic",
                    "comm_pkg/msg/MasterLogic",
                    f'{{header: {{stamp: {{sec: 0, nanosec: 0}}, frame_id: ""}}, '
                    f"as_state: {as_state}, active_mission: {active_mission}}}",
                ]

                try:
                    # Start the process, redirecting output to /dev/null
                    self.publish_process = subprocess.Popen(
                        master_logic_msg,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )

                except Exception as e:
                    print(
                        f"Error starting process: {e}"
                    )  # TODO: thie error handling is not detailed enough

    def stop_publish_masterlogic(self):
        """
        Stop publishing a message to a ROS topic.

        Returns:
            dict: Stopping status
        """
        with self.publish_lock:
            if self.publish_process and self.publish_process.poll() is None:
                try:
                    self.publish_process.terminate()
                    self.publish_process.wait(timeout=2.0)
                    return {"status": "success", "message": "Publishing stopped successfully"}
                except Exception as e:
                    raise HTTPException(
                        status_code=500, detail=str(e)
                    )  # TODO: thie error handling is not detailed enough
            else:
                raise HTTPException(
                    status_code=400, detail="No master logic is currently being published"
                )  # TODO: thie error handling is not detailed enough
