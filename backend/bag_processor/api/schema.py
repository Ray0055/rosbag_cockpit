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


def from_dict_to_rosbag(data: dict) -> List[Rosbag]:
    """
    Convert a dictionary to a list of Rosbag objects.

    Args:
        data: Dictionary containing rosbag data

    Returns:
        List of Rosbag objects
    """
    print("Data:", data)
    return [Rosbag(**item) for item in data]


# def get_rosbag()
