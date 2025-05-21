"""
Database operations for the Cockpit application.

This module provides functions to interact with the SQLite database,
including connecting, inserting, updating, and querying data.
"""

import json
from typing import Any, Dict, List, Optional

from sqlalchemy.sql import text

from .db_connection_pool import DBConnectionPool
from .modles import RosbagMetadata
from .schema import DatabaseSchema


class DatabaseManager:
    """Manages database operations for the Cockpit application."""

    def __init__(self, db_conn_pool: DBConnectionPool):
        """
        Initialize the database manager.

        Args:
            db_path: Path to the SQLite database file
        """
        self.conn_pool = db_conn_pool

    def close_db(self) -> None:
        """
        Close the database connection pool.
        This should be called when the application is shutting down.
        """
        self.conn_pool.dispose()
        print("Database connection pool closed.")

    def add_column_if_not_exists(self, column_name: str, data_type: str = "TEXT") -> bool:
        """
        Add a new column to the rosbags table if it doesn't already exist.

        Args:
            column_name: Name of the column to add
            data_type: SQLite data type for the column

        Returns:
            True if a new column was added, False otherwise
        """
        with self.conn_pool.get_connection() as conn:
            result = DatabaseSchema.add_column_if_not_exists(conn, column_name, data_type)
            if result:
                conn.commit()
                print(f"Added new column: {column_name} ({data_type})")
            return result

    def insert_rosbag_metadata(self, metadata: RosbagMetadata) -> None:
        """
        Insert or update ROS bag metadata in the database.

        Args:
            metadata: RosbagMetadata object containing the data to insert
        """
        metadata_dict = metadata.to_dict()

        # Check for additional metadata fields that might need new columns
        additional_metadata = json.loads(metadata_dict.get("metadata_json", "{}"))
        for key, value in additional_metadata.items():
            data_type = DatabaseSchema.determine_sqlite_type(value)
            self.add_column_if_not_exists(key, data_type)
            metadata_dict[key] = value

        with self.conn_pool.get_connection() as conn:
            # Build the INSERT statement dynamically based on available columns
            columns = DatabaseSchema.get_existing_columns(conn)
            valid_columns = [
                col for col in columns if col in metadata_dict or col == "id" or col == "created_at"
            ]

            column_names = ", ".join(
                [col for col in valid_columns if col != "id" and col != "created_at"]
            )
            placeholders = ", ".join(["?"] * (len(valid_columns) - 2))  # Exclude id and created_at

            params = {}
            column_list = []

            for col in valid_columns:
                if col != "id" and col != "created_at":
                    column_list.append(col)
                    params[col] = metadata_dict.get(col)

            placeholders = ", ".join([f":{col}" for col in column_list])

            sql = text(
                f"""
            INSERT INTO rosbags ({column_names})
            VALUES ({placeholders})
            """
            )

            conn.execute(sql, params)
            conn.commit()
            print(f"Added/updated bag file in database: {metadata_dict['file_path']}")

    def get_rosbag_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get a rosbag entry by its file path.

        Args:
            file_path: Path to the ROS bag file

        Returns:
            Dictionary containing the rosbag data, or None if not found
        """
        with self.conn_pool.get_connection() as conn:
            res = conn.execute(
                text("SELECT * FROM rosbags WHERE file_path = :file_path"), {"file_path": file_path}
            )
            row = res.fetchone()
            if row:
                return dict(row._mapping)
            return None

    def get_all_rosbags(self) -> List[Dict[str, Any]]:
        """
        Get all rosbag entries.

        Returns:
            List of dictionaries containing rosbag data
        """
        with self.conn_pool.get_connection() as conn:
            res = conn.execute(text("SELECT * FROM rosbags"))
            rows = res.fetchall()
            return [dict(row._mapping) for row in rows]

    def get_rosbags_by_map_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all rosbag entries for a specific map category.

        Args:
            category: Map category to filter by

        Returns:
            List of dictionaries containing rosbag data
        """
        with self.conn_pool.get_connection() as conn:
            res = conn.execute(
                text("SELECT * FROM rosbags WHERE map_category = :category"), {"category": category}
            )
            rows = res.fetchall()
            return [dict(row._mapping) for row in rows]

    # def delete_rosbag(self, file_path: str) -> bool:
    #     """
    #     Delete a rosbag entry from the database.

    #     Args:
    #         file_path: Path to the ROS bag file to delete

    #     Returns:
    #         True if an entry was deleted, False otherwise
    #     """
    #     self.cursor.execute("DELETE FROM rosbags WHERE file_path = ?", (file_path,))
    #     deleted = self.cursor.rowcount > 0
    #     self.conn.commit()
    #     return deleted

    def get_database_stats(self) -> Dict[str, Any]:
        """Print statistics about the database."""

        try:
            with self.conn_pool.get_connection() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM rosbags"))
                rosbag_count = result.scalar()

                result = conn.execute(
                    text("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='rosbags'")
                )
                total_columns = result.scalar()

                # TODO: return category counts like:
                # skidpad: 5
                # acceleration: 3

                # result = conn.execute(
                #     "SELECT map_category, COUNT(*) FROM rosbags GROUP BY map_category"
                # )
                # category_counts = result.fetchall()

                return {
                    "rosbag_count": rosbag_count,
                    "total_columns": total_columns,
                }
        except Exception as e:
            print(f"Error occurred while getting database stats: {e}")
            return {
                "rosbag_count": -1,  # Placeholder for error
                "total_columns": -1,
            }
