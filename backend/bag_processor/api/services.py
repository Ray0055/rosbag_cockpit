import asyncio
import io
import logging
import os
import subprocess
import tarfile
import threading
import time
from typing import Any, Dict, List

from docker.errors import DockerException, ImageNotFound
from fastapi import HTTPException

from ..api.schema import Rosbag, from_dict_to_database_stats, from_dicts_to_rosbags
from ..database.operations import DatabaseManager
from .models import DockerContainerConfig, DockerContainerInfo, DockerImageInfo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="bag_processor/api/logs/services.log",
    filemode="a",
)

dbService_logger = logging.getLogger("db_service")
docker_service_logger = logging.getLogger("docker_service")
bag_player_logger = logging.getLogger("bag_player")
open_loop_test_logger = logging.getLogger("open_loop_test")


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

    def container_name_exists(self, container_name: str) -> bool:
        """
        Check if a Docker container exists by name.
        """
        try:
            containers = self.docker_client.containers.list(
                all=True, filters={"name": container_name}
            )
            return len(containers) > 0
        except DockerException as e:
            docker_service_logger.error(f"Docker Error in checking container: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            docker_service_logger.error(f"Error in checking container: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def check_container_exists_by_id(self, container_id: str) -> bool:
        """
        Check if a Docker container exists by ID.

        Args:
            container_id: Docker container ID

        Returns:
            bool: True if container exists, False otherwise
        """
        try:
            self.docker_client.containers.get(container_id)
            return True
        except DockerException as e:
            docker_service_logger.error(f"Docker Error in checking container: {str(e)}")

            if "No such container" in str(e):
                return False

            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            docker_service_logger.error(f"Error in checking container: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def check_image_exists(self, image_tag: str) -> bool:
        """
        Check if a Docker image exists by its tag.

        Args:
            image_tag: Docker image tag

        Returns:
            bool: True if image exists, False otherwise
        """
        try:
            self.docker_client.images.get(image_tag)
            return True
        except ImageNotFound:
            docker_service_logger.error(f"Image '{image_tag}' not found")
            return False
        except DockerException as e:
            docker_service_logger.error(f"Docker Error in checking image: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            docker_service_logger.error(f"Error in checking image: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def run_container_from_image(self, image_tag: str, config: DockerContainerConfig):
        """
        Run a Docker container with the specified image tag.

        Args:
            image_tag: Docker image tag

        Returns:
            dict: Container details
        """
        try:
            if config.name and self.container_name_exists(config.name):
                docker_service_logger.error(f"Container with name '{config.name}' already exists")
                raise HTTPException(
                    status_code=409, detail=f"Container with name '{config.name}' already exists"
                )
            docker_service_logger.info(f"Started running container with image '{image_tag}'")
            if self.check_image_exists(image_tag):
                container = self.docker_client.containers.run(
                    image_tag,
                    detach=True,
                    name=config.name,
                    volumes=config.volumes,
                    ports=config.ports,
                    environment=config.environment,
                    command=config.command,
                    network=config.network,
                    user="1000:1000",  # use the same user as the host
                )
                docker_service_logger.info(f"Container started with ID: {container.id}")
                return {"status": "success", "container_id": container.id}
        except ImageNotFound as e:
            docker_service_logger.error(f"Error: Image '{image_tag}' not found. Details: {str(e)}")
            raise HTTPException(status_code=404, detail=str(e))

        except DockerException as e:
            docker_service_logger.error(f"Docker Error: {str(e)}")
            raise HTTPException(status_code=501, detail=str(e))

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def run_container_by_id(self, container_id: str):
        """
        Run a Docker container by ID.

        Args:
            container_id: Docker container ID

        Returns:
            dict: Running status
        """
        try:
            if self.check_container_exists_by_id(container_id):
                container = self.docker_client.containers.get(container_id)
                container.start()
                return {
                    "status": "success",
                    "message": f"Container {container_id} started successfully",
                }
            else:
                docker_service_logger.error(f"Container with ID '{container_id}' not found")
                raise HTTPException(status_code=404, detail=f"No such container: {container_id}")
        except HTTPException:
            # Re-raise HTTPException, maintaining the original status code
            raise
        except Exception as e:
            docker_service_logger.error(f"Error starting container {container_id}: {str(e)}")
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
        # If you have problems while removing the container which was created with
        # create_container_from_image, you can try to following command:
        # sudo aa-remove-unknown
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

    def copy_from_container(self, container_id: str, source_path: str, dest_path: str):
        """
        Copy files from a Docker container to the host.

        Args:
            container_id: Docker container ID
            source_path: Source path in the container
            dest_path: Destination path on the host

        Returns:
            dict: Copying status
        """
        try:
            container = self.docker_client.containers.get(container_id)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            bits, stat = container.get_archive(source_path)

            tar_stream = io.BytesIO()
            for chunk in bits:
                tar_stream.write(chunk)
            tar_stream.seek(0)

            with tarfile.open(fileobj=tar_stream) as tar:
                tar.extractall(path=dest_path)

            return {
                "status": "success",
                "message": f"Files copied from container: {container_id} from"
                f"{source_path} to {dest_path} successfully",
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


class OpenLoopTestService:
    def __init__(self, docker_service, bag_player, database_service=None):
        self.docker_service = docker_service
        self.bag_player = bag_player
        self.database_service = database_service

    async def execute_open_loop_test(
        self,
        rosbag_paths: List[str],
        image_tag: str,
    ) -> Dict[str, Any]:
        """
        Execute complete open loop test process, directly calling service functions

        Args:
            rosbag_paths: List of rosbag file paths to process
            image_tag: Docker image tag to run

        Returns:
            Dict: Dictionary containing operation results
        """
        container_id = None
        results = []
        try:
            # Validate all rosbag paths
            for path in rosbag_paths:
                if not os.path.exists(path):
                    raise ValueError(f"Rosbag file does not exist: {path}")

            # 1. Start Docker container
            container_config = DockerContainerConfig(
                name="workspace",
                network="host",
                command=[
                    "/bin/bash",
                    "-c",
                    "source scripts/launch/launch_all_sim.bash && tail -f /dev/null",
                ],
            )
            container_response = self.docker_service.run_container_from_image(
                image_tag, container_config
            )
            container_id = container_response.get("container_id")
            open_loop_test_logger.info(f"Started Docker container with ID: {container_id}")

            # 2. Process each rosbag file
            for i, rosbag_path in enumerate(rosbag_paths):
                open_loop_test_logger.info(
                    f"Processing rosbag {i+1}/{len(rosbag_paths)}: {rosbag_path}"
                )

                # Play rosbag
                self.bag_player.play_bag(rosbag_path)
                time.sleep(2)  # must wait for rosbag starting to playback
                # Wait for rosbag playback to finish
                while True:
                    status = self.bag_player.get_playback_status()

                    if not status.get("running", False):
                        break
                    else:
                        open_loop_test_logger.info(f"Rosbag {rosbag_path} is still playing...")
                    await asyncio.sleep(5)  # Use async sleep

                # Stop playback
                self.bag_player.stop_playback()

                # Record results
                results.append({"rosbag": rosbag_path, "status": "completed", "index": i + 1})

                # If not the last rosbag, restart container
                if i < len(rosbag_paths) - 1:
                    self.docker_service.stop_container_by_id(container_id)
                    self.docker_service.run_container_by_id(container_id)
                    open_loop_test_logger.info(
                        f"Restarted Docker container with ID: {container_id}"
                    )

            # 3. After processing all rosbags, copy evaluation data
            self.docker_service.stop_container_by_id(container_id)

            # Copy lidar evaluation data
            lidar_output_path = "/home/carmaker/tmp/output/lidar"
            self.docker_service.copy_from_container(
                container_id,
                "/home/vscode/workspace/src/lidar/evaluation/",  # username is set up in Dockerfile
                f"{lidar_output_path}",
            )

            # Copy estimation evaluation data
            estimation_output_path = "/home/carmaker/tmp/output/estimation"
            self.docker_service.copy_from_container(
                container_id,
                "/home/vscode/workspace/src/estimation/evaluation/",
                f"{estimation_output_path}",
            )

            open_loop_test_logger.info("Copied evaluation data from container to host")
            time.sleep(2)
            # 4. Delete container
            self.docker_service.remove_container_by_id(container_id)
            open_loop_test_logger.info(f"Deleted Docker container with ID: {container_id}")
            return {
                "success": True,
                "message": "Open loop test completed successfully",
                "container_id": container_id,
                "results": results,
                "output_paths": [
                    f"{lidar_output_path}",
                    f"{estimation_output_path}",
                ],
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Open loop test failed: {str(e)}",
                "error": str(e),
            }

    async def analyze_rosbag(
        self,
        evaluation_folder_path: str,
        script_path: str,
        extra_args: List[str] = None,
    ):
        """
        Analyze the rosbag using a specified script.

        Args:
            evaluation_folder_path: Path to the folder containing evaluation data
            script_path: Path to the analysis script
            extra_args: Additional arguments for the script

        Returns:
            dict: Analysis results
        """
        try:
            # Check if the script exists
            if not os.path.exists(script_path):
                open_loop_test_logger.error(f"Script file does not exist: {script_path}")
                raise ValueError(f"Script file does not exist: {script_path}")

            # Check if the evaluation folder exists
            if not os.path.exists(evaluation_folder_path):
                open_loop_test_logger.error(
                    f"Evaluation folder does not exist: {evaluation_folder_path}"
                )
                raise ValueError(f"Evaluation folder does not exist: {evaluation_folder_path}")

            if extra_args is None:
                extra_args = []

            # Run the analysis script
            cmd = ["/usr/bin/python3", os.path.basename(script_path)] + extra_args
            open_loop_test_logger.info(f"Evaluation folder: {evaluation_folder_path}")
            open_loop_test_logger.info(f"Running analysis script: {' '.join(cmd)}")

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=evaluation_folder_path,
                )

                if result.returncode != 0:
                    error_msg = (
                        f"Script execution failed with return code "
                        f"{result.returncode}: {result.stderr}"
                    )
                    open_loop_test_logger.error(error_msg)
                    raise RuntimeError(error_msg)

                open_loop_test_logger.info("Analysis completed successfully")
                return {
                    "status": "success",
                    "message": "Analysis completed successfully",
                    "output": result.stdout,
                }

            except FileNotFoundError as e:
                error_msg = f"The program or script was not found: {e}"
                open_loop_test_logger.error(error_msg)
                raise RuntimeError(error_msg)

            except PermissionError as e:
                error_msg = f"Permission denied: {e}"
                open_loop_test_logger.error(error_msg)
                raise RuntimeError(error_msg)

            except subprocess.TimeoutExpired as e:
                error_msg = f"Command timed out: {e}"
                open_loop_test_logger.error(error_msg)
                raise RuntimeError(error_msg)

        except Exception as e:
            open_loop_test_logger.exception(f"Error in analyze_rosbag: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
