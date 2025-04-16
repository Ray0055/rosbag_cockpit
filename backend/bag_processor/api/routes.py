"""
API routes for the RosBag Cockpit application.
This module defines all the API endpoints for managing and analyzing ROS bag files.
"""

from typing import Dict, List, Union

import docker
from fastapi import APIRouter, Body, Path, Query

from bag_processor.api.models import Rosbag

from ..bag_manager.player import RosbagPlayer
from ..database.db_connection_pool import DBConnectionPool
from ..database.operations import DatabaseManager
from .models import DockerContainerConfig
from .services import DatabaseService, DockerService, RosPublisherService

router = APIRouter(prefix="/api")

# Create connection pool
db_conn_pool = DBConnectionPool(
    db_url="sqlite:///rosbag_metadata.db",
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
)

# Create database manager with the connection pool
db_manager = DatabaseManager(db_conn_pool=db_conn_pool)
database_service = DatabaseService(db_manager)

bag_player = RosbagPlayer()

# Initializattion of docker client
docker_client = docker.from_env()
docker_service = DockerService(docker_client)
publish_service = RosPublisherService()


@router.get("/", response_model=Dict[str, str])
async def root():
    """
    Root endpoint to check if the API is running.

    Returns:
        Dict[str, str]: A welcome message
    """
    return {"message": "Welcome to RosBag Cockpit API"}


@router.get(
    "/stats",
)
async def get_database_stats():
    """
    Get system statistics.

    Args:
        db (Session): Database session

    Returns:
        Stats: System statistics
    """

    return database_service.get_database_stats()


@router.get("/rosbags/{map_category}", response_model=List[Rosbag])
async def get_rosbags_by_map_category(
    map_category: str = Path(..., title="The map category to filter by"),
):
    """
    Get skidpad rosbags.

    Args:
        db (Session): Database session

    Returns:
        List[Rosbag]: List of skidpad rosbags
    """

    return database_service.get_rosbags_by_map_category(map_category)


@router.post("/rosbags/view", response_model=Rosbag)
async def create_rosbag_endpoint():
    """
    Create a new rosbag entry.

    Args:
        rosbag (RosbagCreate): Rosbag data
        db (Session): Database session

    Returns:
        Rosbag: The created rosbag
    """
    pass


@router.post("/rosbags/upload", response_model=Rosbag)
async def upload_rosbag(
    # file: UploadFile = File(...),
    # name: str = Form(...),
    # description: Optional[str] = Form(None),
    # tags: Optional[str] = Form(None),
    # db: Session = Depends(get_db)
):
    """
    Upload a new rosbag file and create an entry for it.

    Args:
        file (UploadFile): The rosbag file to upload
        name (str): Name of the rosbag
        description (Optional[str]): Description of the rosbag
        tags (Optional[str]): Comma-separated list of tags
        db (Session): Database session

    Returns:
        Rosbag: The created rosbag
    """
    pass


@router.get("/rosbags", response_model=List[Rosbag])
async def get_rosbags_endpoint(
    # skip: int = 0,
    # limit: int = 100,
    # search: Optional[str] = None,
    # tag: Optional[str] = None,
):
    """
    Get a list of rosbags.

    Args:
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return
        search (Optional[str]): Search term for filtering rosbags
        tag (Optional[str]): Filter rosbags by tag
        db (Session): Database session

    Returns:
        List[Rosbag]: List of rosbags
    """
    return database_service.get_all_rosbags()


@router.get("/rosbags/{rosbag_id}", response_model=Rosbag)
async def get_rosbag_endpoint(
    rosbag_id: int = Path(..., title="The ID of the rosbag to get"),
):
    """
    Get a rosbag by ID.

    Args:
        rosbag_id (int): ID of the rosbag
        db (Session): Database session

    Returns:
        Rosbag: The rosbag
    """
    pass


@router.delete(
    "/rosbags/{rosbag_id}",
)
async def delete_rosbag_endpoint(
    rosbag_id: int = Path(..., title="The ID of the rosbag to delete"),
):
    """
    Delete a rosbag.

    Args:
        rosbag_id (int): ID of the rosbag to delete
        db (Session): Database session

    Returns:
        SuccessResponse: Success message
    """
    pass


@router.get(
    "/rosbags/{rosbag_id}/topics",
)
async def get_topics_endpoint(
    rosbag_id: int = Path(..., title="The ID of the rosbag"),
):
    """
    Get topics for a rosbag.

    Args:
        rosbag_id (int): ID of the rosbag
        db (Session): Database session

    Returns:
        List[Topic]: List of topics
    """
    pass


@router.post(
    "/rosbags/play/start",
)
async def play_rosbag_endpoint(
    bag_path: Union[str, None] = Query(default=None, title="The ID of the rosbag to play"),
):
    """
    Start playing a rosbag.

    Args:
        rosbag_id (int): ID of the rosbag
        db (Session): Database session

    Returns:
        SuccessResponse: Success message
    """
    # Check if the rosbag exists
    rosbag = database_service.get_rosbag_by_path_or_404(bag_path)

    bag_player.play_bag(rosbag.file_path)

    return {"message": "Started playing rosbag ''", "data": None}


@router.post(
    "/rosbags/play/stop",
)
async def stop_play_rosbag_endpoint():
    """
    Stop playing a rosbag.

    Args:
        rosbag_id (int): ID of the rosbag
        db (Session): Database session

    Returns:
        SuccessResponse: Success message
    """
    res = bag_player.stop_playback()

    return {"message": f"{res}"}


@router.post(
    "/rosbags/play/status",
)
async def get_play_rosbag_status_endpoint():
    """
    Get the status of the rosbag player.

    Args:
        rosbag_id (int): ID of the rosbag
        db (Session): Database session

    Returns:
        SuccessResponse: Success message
    """
    status = bag_player.get_playback_status()

    return status


@router.post(
    "/docker/run/{image_tag}",
)
async def run_container_endpoint(
    image_tag: str = Path(..., title="The Docker image tag to run"),
    config: DockerContainerConfig = Body(default=None, title="Docker container configuration"),
):
    """
    Run a Docker container with the specified image tag.

    Args:
        image_tag (str): The Docker image tag to run
        db (Session): Database session

    Returns:
        SuccessResponse: Success message
    """
    if config is None:
        config = DockerContainerConfig()
    return docker_service.run_container_from_image(image_tag, config)


@router.get(
    "/docker/run/{container_id}",
)
async def run_container_by_id_endpoint(
    container_id: str = Path(..., title="The Docker container ID to run"),
):
    """
    Run a Docker container with the specified container ID.
    Args:
        container_id (str): The Docker container ID to run
    Returns:
        SuccessResponse: Success message
    """
    return docker_service.run_container_by_id(container_id)


@router.post(
    "/docker/stop/{container_id}",
)
async def stop_container_endpoint(
    container_id: str = Path(..., title="The Docker container ID to stop"),
):
    """
    Stop a running Docker container.

    Args:
        container_id (str): The Docker container ID to stop
    Returns:
        SuccessResponse: Success message
    """
    return docker_service.stop_container_by_id(container_id)


@router.delete(
    "/docker/remove/{container_id}",
)
async def remove_container_endpoint(
    container_id: str = Path(..., title="The Docker container ID to remove"),
):
    """
    Remove a Docker container.

    Args:
        container_id (str): The Docker container ID to remove
    Returns:
        SuccessResponse: Success message
    """
    return docker_service.remove_container_by_id(container_id)


@router.get(
    "/docker/images",
)
async def list_docker_images_endpoint():
    """
    List all Docker images.

    Returns:
        List[Dict[str, str]]: List of Docker images
    """
    return docker_service.list_all_images()


@router.get(
    "/docker/containers",
)
async def list_docker_containers_endpoint():
    """
    List all Docker containers.

    Returns:
        List[Dict[str, str]]: List of Docker containers
    """
    return docker_service.list_all_containers()


@router.post(
    "/topics/master_logic/publish",
)
async def publish_topic_endpoint(as_state: int, active_mission: int):
    """
    Publish a message from ROS topic.

    Args:
        topic (str): The topic to publish
        message (str): The message to publish

    Returns:
        SuccessResponse: Success message
    """
    return publish_service.publish_masterlogic(as_state, active_mission)


@router.post(
    "/topics/master_logic/stop",
)
async def stop_publish_topic_endpoint():
    """
    Stop publishing a message from ROS topic.

    Args:
        topic (str): The topic to publish
        message (str): The message to publish

    Returns:
        SuccessResponse: Success message
    """
    return publish_service.stop_publish_masterlogic()
