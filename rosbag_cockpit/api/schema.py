from .models import DatabaseStats


def from_dict_to_database_stats(data: dict) -> DatabaseStats:
    """
    Convert a dictionary to a DatabaseStats object.

    Args:
        data: Dictionary containing database statistics

    Returns:
        DatabaseStats object
    """
    return DatabaseStats(**data)
