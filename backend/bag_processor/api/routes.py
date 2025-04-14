"""
API routes for the RosBag Cockpit application.
This module defines all the API endpoints for managing and analyzing ROS bag files.
"""

from typing import Dict, List, Union

from fastapi import APIRouter, Depends, Path, Query
from .services import DatabaseService
from bag_processor.api.models import Rosbag
from ..bag_manager.player import RosbagPlayer
# from cockpit.api.utils import (
#     load_config,
#     validate_rosbag_path,
#     get_rosbag_or_404,
#     analyze_rosbag_file,
# )
# from cockpit.rosbag.parser import get_messages_by_topics
# from cockpit.rosbag.player import RosbagPlayer
from ..database.operations import DatabaseManager
from .schema import from_dict_to_database_stats, from_dicts_to_rosbags
from ..database.db_connection_pool import DBConnectionPool
router = APIRouter(prefix="/api")

# Create connection pool
db_conn_pool = DBConnectionPool(
    db_url="sqlite:///rosbag_metadata.db",
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800
)

# Create database manager with the connection pool
db_manager = DatabaseManager(db_conn_pool=db_conn_pool)
database_service = DatabaseService(db_manager)


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
async def get_system_stats():
    """
    Get system statistics.

    Args:
        db (Session): Database session

    Returns:
        Stats: System statistics
    """

    return database_service.get_database_stats()


@router.get(
    "/rosbags/{map_category}", response_model=List[Rosbag]
)
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


# # Rosbag endpoints
# @router.post("/rosbags/view", response_model=Rosbag)
# async def create_rosbag_endpoint(
#     rosbag: RosbagCreate,
#     db: Session = Depends(get_db)
# ):
#     """
#     Create a new rosbag entry.

#     Args:
#         rosbag (RosbagCreate): Rosbag data
#         db (Session): Database session

#     Returns:
#         Rosbag: The created rosbag
#     """
#     # Validate that the rosbag file exists
#     path = validate_rosbag_path(rosbag.path)

#     # Analyze the rosbag file to get metadata
#     info = analyze_rosbag_file(str(path))

#     # Create the rosbag entry
#     db_rosbag = create_rosbag(db, rosbag, info)

#     # Create topic entries for each topic in the rosbag
#     for topic_info in info.get("topics", []):
#         topic_data = TopicCreate(
#             rosbag_id=db_rosbag.id,
#             name=topic_info["name"],
#             message_type=topic_info["type"],
#             message_count=topic_info["message_count"],
#             frequency=topic_info.get("frequency"),
#         )
#         create_topic(db, topic_data)

#     return db_rosbag


# @router.post("/rosbags/upload", response_model=Rosbag)
# async def upload_rosbag(
#     file: UploadFile = File(...),
#     name: str = Form(...),
#     description: Optional[str] = Form(None),
#     tags: Optional[str] = Form(None),
#     db: Session = Depends(get_db)
# ):
#     """
#     Upload a new rosbag file and create an entry for it.

#     Args:
#         file (UploadFile): The rosbag file to upload
#         name (str): Name of the rosbag
#         description (Optional[str]): Description of the rosbag
#         tags (Optional[str]): Comma-separated list of tags
#         db (Session): Database session

#     Returns:
#         Rosbag: The created rosbag
#     """
#     if not file.filename.endswith(".bag"):
#    raise HTTPException(status_code=400, detail="Uploaded file must be a .bag file")

#     # Parse tags
#     tag_list = []
#     if tags:
#         tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

#     # Save the uploaded file
#     config = load_config()
#     storage_dir = config["rosbag"]["storage_dir"]
#     os.makedirs(storage_dir, exist_ok=True)

#     file_path = os.path.join(storage_dir, file.filename)

#     # Write the file to disk
#     with open(file_path, "wb") as buffer:
#         while True:
#             chunk = await file.read(1024 * 1024)  # Read 1MB at a time
#             if not chunk:
#                 break
#             buffer.write(chunk)

#     # Create the rosbag entry
#     rosbag_data = RosbagCreate(
#         name=name,
#         description=description,
#         path=file_path,
#         tags=tag_list
#     )

#     # Analyze and create the rosbag entry
#     info = analyze_rosbag_file(file_path)
#     db_rosbag = create_rosbag(db, rosbag_data, info)

#     # Create topic entries
#     for topic_info in info.get("topics", []):
#         topic_data = TopicCreate(
#             rosbag_id=db_rosbag.id,
#             name=topic_info["name"],
#             message_type=topic_info["type"],
#             message_count=topic_info["message_count"],
#             frequency=topic_info.get("frequency"),
#         )
#         create_topic(db, topic_data)

#     return db_rosbag


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



# @router.get("/rosbags/{rosbag_id}", response_model=Rosbag)
# async def get_rosbag_endpoint(
#     rosbag_id: int = Path(..., title="The ID of the rosbag to get"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Get a rosbag by ID.

#     Args:
#         rosbag_id (int): ID of the rosbag
#         db (Session): Database session

#     Returns:
#         Rosbag: The rosbag
#     """
#     return get_rosbag_or_404(db, rosbag_id)


# @router.put("/rosbags/{rosbag_id}", response_model=Rosbag)
# async def update_rosbag_endpoint(
#     rosbag_update: RosbagUpdate,
#     rosbag_id: int = Path(..., title="The ID of the rosbag to update"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Update a rosbag.

#     Args:
#         rosbag_update (RosbagUpdate): Updated rosbag data
#         rosbag_id (int): ID of the rosbag to update
#         db (Session): Database session

#     Returns:
#         Rosbag: The updated rosbag
#     """
#     # Check if the rosbag exists
#     get_rosbag_or_404(db, rosbag_id)

#     # Update the rosbag
#     return update_rosbag(db, rosbag_id, rosbag_update)


# @router.delete("/rosbags/{rosbag_id}", response_model=SuccessResponse)
# async def delete_rosbag_endpoint(
#     rosbag_id: int = Path(..., title="The ID of the rosbag to delete"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Delete a rosbag.

#     Args:
#         rosbag_id (int): ID of the rosbag to delete
#         db (Session): Database session

#     Returns:
#         SuccessResponse: Success message
#     """
#     # Check if the rosbag exists
#     rosbag = get_rosbag_or_404(db, rosbag_id)

#     # Delete the rosbag
#     delete_rosbag(db, rosbag_id)

#     return {"message": f"Rosbag '{rosbag.name}' deleted successfully", "data": None}


# @router.get("/rosbags/{rosbag_id}/topics", response_model=List[Topic])
# async def get_topics_endpoint(
#     rosbag_id: int = Path(..., title="The ID of the rosbag"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Get topics for a rosbag.

#     Args:
#         rosbag_id (int): ID of the rosbag
#         db (Session): Database session

#     Returns:
#         List[Topic]: List of topics
#     """
#     # Check if the rosbag exists
#     get_rosbag_or_404(db, rosbag_id)

#     # Get topics
#     return get_topics_by_rosbag_id(db, rosbag_id)


# @router.post("/rosbags/{rosbag_id}/messages", response_model=List[Message])
# async def get_messages_endpoint(
#     query: MessageQuery,
#     rosbag_id: int = Path(..., title="The ID of the rosbag"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Get messages from a rosbag.

#     Args:
#         query (MessageQuery): Query parameters
#         rosbag_id (int): ID of the rosbag
#         db (Session): Database session

#     Returns:
#         List[Message]: List of messages
#     """
#     # Check if the rosbag exists
#     rosbag = get_rosbag_or_404(db, rosbag_id)

#     # Get messages from the rosbag file
#     messages = get_messages_by_topics(
#         rosbag.path,
#         query.topic_names,
#         query.start_time,
#         query.end_time,
#         query.limit,
#         query.offset
#     )

#     return messages


@router.post("/rosbags/play",)
async def play_rosbag_endpoint(
    bag_path: Union[str, None] = Query(
        default=None, title="The ID of the rosbag to play"),):
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

    # Create a player and start playing
    player = RosbagPlayer()
    player.play_bag(rosbag.file_path)

    return {"message": f"Started playing rosbag ''", "data": None}


# @router.post("/rosbags/{rosbag_id}/stop", response_model=SuccessResponse)
# async def stop_rosbag_endpoint(
#     rosbag_id: int = Path(..., title="The ID of the rosbag to stop"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Stop playing a rosbag.

#     Args:
#         rosbag_id (int): ID of the rosbag
#         db (Session): Database session

#     Returns:
#         SuccessResponse: Success message
#     """
#     # Check if the rosbag exists
#     rosbag = get_rosbag_or_404(db, rosbag_id)

#     # Create a player and stop playing
#     player = RosbagPlayer(rosbag.path)
#     player.stop()

#     return {"message": f"Stopped playing rosbag '{rosbag.name}'", "data": None}


# @router.post("/rosbags/{rosbag_id}/analyze", response_model=Dict[str, Any])
# async def analyze_rosbag_endpoint(
#     rosbag_id: int = Path(..., title="The ID of the rosbag to analyze"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Analyze a rosbag file and get detailed information.

#     Args:
#         rosbag_id (int): ID of the rosbag
#         db (Session): Database session

#     Returns:
#         Dict[str, Any]: Detailed information about the rosbag
#     """
#     # Check if the rosbag exists
#     rosbag = get_rosbag_or_404(db, rosbag_id)

#     # Analyze the rosbag file
#     info = analyze_rosbag_file(rosbag.path)

#     return info
