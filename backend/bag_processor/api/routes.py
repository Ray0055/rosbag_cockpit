"""
API routes for the RosBag Cockpit application.
This module defines all the API endpoints for managing and analyzing ROS bag files.
"""

import os
from collections import deque
from typing import Dict, List, Optional, Union

import docker
from fastapi import APIRouter, Body, HTTPException, Path, Query

from bag_processor.api.models import Rosbag

from ..bag_manager.player import RosbagPlayer
from ..database.db_connection_pool import DBConnectionPool
from ..database.operations import DatabaseManager
from .exception_handlers import (
    DockerContainerAccessError,
    DockerContainerGetError,
    DockerContainerNotFoundError,
)
from .logging import LogType, server_logger
from .models import DockerContainerConfig
from .services import DatabaseService, DockerService, OpenLoopTestService, RosPublisherService

router = APIRouter(prefix="/api")

dp_path = os.getenv("DATABASE_PATH")
if dp_path is None:
    raise ValueError("DATABASE_PATH is not set.")

if not os.path.exists(dp_path):
    raise ValueError(f"Database path does not exist: {dp_path}")

# Create connection pool
db_conn_pool = DBConnectionPool(
    db_url=f"sqlite:///{dp_path}",
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
openloop_service = OpenLoopTestService(docker_service, bag_player, database_service)


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
    topics: Optional[List[str]] = Query(default=None, title="List of topics to play"),
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

    bag_player.play_bag(bag_path=rosbag.file_path, topics=topics)

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


@router.post("/docker/run")
async def run_docker_endpoint(
    image_tag: Optional[str] = Query(None, title="The Docker image tag to run"),
    container_id: Optional[str] = Query(None, title="The Docker container ID to run"),
    config: Optional[DockerContainerConfig] = Body(
        default=None, title="Docker container configuration"
    ),
):
    """
    Run a Docker container either with the specified image tag or container ID.

    Args:
        image_tag (Optional[str]): The Docker image tag to run
        container_id (Optional[str]): The Docker container ID to run
        config (Optional[DockerContainerConfig]): Docker container configuration

    Returns:
        SuccessResponse: Success message
    """
    try:
        if image_tag is not None:
            if config is None:
                config = DockerContainerConfig()
            return docker_service.run_container_from_image(image_tag, config)
        elif container_id is not None:
            return docker_service.run_container_by_id(container_id)
    except DockerContainerNotFoundError as e:
        server_logger.error(f"Docker container not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except DockerContainerGetError as e:
        server_logger.error(f"Docker container get error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except DockerContainerAccessError as e:
        server_logger.error(f"Docker container access error: {e}")
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        server_logger.error(f"Unexpected error in run_docker_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


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


@router.post(
    "/docker/copy/{container_id}",
)
async def copy_from_container_endpoint(
    container_id: str = Path(..., title="The Docker container ID to copy to"),
    source_path: str = Body(..., title="The source path to copy from"),
    destination_path: str = Body(..., title="The destination path to copy to"),
):
    """
    Copy files to a Docker container.

    Args:
        container_id (str): The Docker container ID to copy to
        source_path (str): The source path to copy from
        destination_path (str): The destination path to copy to

    Returns:
        SuccessResponse: Success message
    """
    return docker_service.copy_from_container(container_id, source_path, destination_path)


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


@router.post(
    "/test/open_loop",
)
async def run_open_loop_test_endpoint(
    rosbag_paths: List[str] = Body(..., title="The path to the rosbag file"),
    image_tag: str = Body(..., title="The image tag to run"),
):
    """
    Run an open loop test with the specified rosbag and backend URL.

    Args:
        rosbag_path (str): The path to the rosbag file
        backend_url (str): The backend URL

    Returns:
        SuccessResponse: Success message
    """
    result = await openloop_service.execute_open_loop_test(
        rosbag_paths=rosbag_paths,
        image_tag=image_tag,
    )

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])

    return result


@router.post(
    "/test/analyze",
)
async def analyze_rosbag_endpoint(
    evaluation_folder_path: str = Body(..., title="The path to the evaluation folder"),
    script_path: str = Body(..., title="The path to the analysis script"),
    extra_args: List[str] = Body(default=[], title="Additional arguments for the analysis script"),
):
    """
    Analyze a rosbag using a specified script.

    Args:
        evaluation_folder_path (str): The path to the evaluation folder
        script_path (str): The path to the analysis script
        extra_args (List[str]): Additional arguments for the analysis script

    Returns:
        SuccessResponse: Success message
    """
    result = await openloop_service.analyze_rosbag(
        evaluation_folder_path=evaluation_folder_path,
        script_path=script_path,
        extra_args=extra_args,
    )

    if result["status"] != "success":
        raise HTTPException(status_code=500, detail=result["message"])

    return result


@router.get("/logs/{log_type}")
async def get_logs(
    log_type: str = Path(
        ..., title="The type of log to retrieve", enum=[log.value for log in LogType]
    ),
    lines: int = 100,
):
    log_file = f"bag_processor/api/logs/{log_type}.log"
    if not os.path.exists(log_file):
        raise HTTPException(status_code=404, detail=f"Log file {log_type} not found")

    try:
        with open(log_file, "r") as f:
            last_lines = list(deque(f, maxlen=lines))
        return {"logs": last_lines}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading logs: {str(e)}")
