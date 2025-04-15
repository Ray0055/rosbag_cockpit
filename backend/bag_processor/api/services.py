from typing import List

from fastapi import HTTPException

from ..api.schema import Rosbag, from_dict_to_database_stats, from_dicts_to_rosbags
from ..database.operations import DatabaseManager
from .models import DockerContainerInfo, DockerImageInfo


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

    def run_container_from_image(self, image_tag: str):
        """
        Run a Docker container with the specified image tag.

        Args:
            image_tag: Docker image tag

        Returns:
            dict: Container details
        """
        try:
            container = self.docker_client.containers.run(image_tag, detach=True)
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

    def delete_container_from_id(self, container_id: str):
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

    def stop_container_from_id(self, container_id: str):
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
