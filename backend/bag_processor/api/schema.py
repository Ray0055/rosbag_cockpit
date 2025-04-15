from typing import List

from .models import DatabaseStats, Rosbag


def from_dict_to_database_stats(data: dict) -> DatabaseStats:
    """
    Convert a dictionary to a DatabaseStats object.

    Args:
        data: Dictionary containing database statistics

    Returns:
        DatabaseStats object
    """
    return DatabaseStats(**data)


def from_dicts_to_rosbags(data: List[dict]) -> List[Rosbag]:
    """
    Convert a dictionary to a list of Rosbag objects.

    Args:
        data: Dictionary containing rosbag data

    Returns:
        List of Rosbag objects
    """
    return [Rosbag(**item) for item in data]


def get_all_rosbags(db) -> List[Rosbag]:
    """
    Get all rosbags from the database.

    Args:
        db: Database session

    Returns:
        List of Rosbag objects
    """
    # Placeholder for actual database query
    # data = db.get_all_rosbags()
    # return from_dict_to_rosbag(data)
    pass


# def get_rosbag()
