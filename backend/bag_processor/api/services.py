
from typing import List
from fastapi import HTTPException
from ..database.operations import DatabaseManager
from ..api.schema import from_dict_to_database_stats, from_dicts_to_rosbags
from ..api.schema import DatabaseStats, Rosbag
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
    
    def  get_rosbags_by_map_category(self, map_category: str):
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
            raise HTTPException(
                status_code=404, detail=f"Rosbag with path {bag_path} not found"
            )
        return from_dicts_to_rosbags([rosbag])[0]