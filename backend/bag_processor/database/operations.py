"""
Database operations for the Cockpit application.

This module provides functions to interact with the SQLite database,
including connecting, inserting, updating, and querying data.
"""

import json
import sqlite3
from typing import Any, Dict, List, Optional

from .modles import RosbagMetadata
from .schema import DatabaseSchema


class DatabaseManager:
    """Manages database operations for the Cockpit application."""

    DEFAULT_DB_PATH = "rosbag_metadata.db"

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        """
        Initialize the database manager.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect_db()
        self.initialize_db()

    def connect_db(self) -> None:
        """Connect to the SQLite database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def close_db(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()

    def initialize_db(self) -> None:
        """Initialize the database schema."""
        DatabaseSchema.initialize_database(self.cursor)
        self.conn.commit()

    def get_db(self):
        """
        Get a database connection for dependency injection.
        Creates a new connection for each request to avoid thread safety issues.

        Yields:
            sqlite3.Connection: Database connection that will be closed after use
        """
        # Create a new connection for each request instead of using self.conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def add_column_if_not_exists(self, column_name: str, data_type: str = "TEXT") -> bool:
        """
        Add a new column to the rosbags table if it doesn't already exist.

        Args:
            column_name: Name of the column to add
            data_type: SQLite data type for the column

        Returns:
            True if a new column was added, False otherwise
        """
        result = DatabaseSchema.add_column_if_not_exists(self.cursor, column_name, data_type)
        if result:
            self.conn.commit()
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

        # Build the INSERT statement dynamically based on available columns
        columns = DatabaseSchema.get_existing_columns(self.cursor)
        valid_columns = [
            col for col in columns if col in metadata_dict or col == "id" or col == "created_at"
        ]

        column_names = ", ".join(
            [col for col in valid_columns if col != "id" and col != "created_at"]
        )
        placeholders = ", ".join(["?"] * (len(valid_columns) - 2))  # Exclude id and created_at

        values = [
            metadata_dict.get(col) for col in valid_columns if col != "id" and col != "created_at"
        ]

        sql = f"""
        INSERT INTO rosbags ({column_names})
        VALUES ({placeholders})
        """

        self.cursor.execute(sql, values)
        self.conn.commit()
        print(f"Added/updated bag file in database: {metadata_dict['file_path']}")

    def get_rosbag_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get a rosbag entry by its file path.

        Args:
            file_path: Path to the ROS bag file

        Returns:
            Dictionary containing the rosbag data, or None if not found
        """
        self.cursor.execute("SELECT * FROM rosbags WHERE file_path = ?", (file_path,))
        row = self.cursor.fetchone()

        if row:
            return dict(row)
        return None

    def get_all_rosbags(self) -> List[Dict[str, Any]]:
        """
        Get all rosbag entries.

        Returns:
            List of dictionaries containing rosbag data
        """
        self.cursor.execute("SELECT * FROM rosbags")
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]

    def get_rosbags_by_map_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all rosbag entries for a specific map category.

        Args:
            category: Map category to filter by

        Returns:
            List of dictionaries containing rosbag data
        """
        self.cursor.execute("SELECT * FROM rosbags WHERE map_category = ?", (category,))
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]

    def delete_rosbag(self, file_path: str) -> bool:
        """
        Delete a rosbag entry from the database.

        Args:
            file_path: Path to the ROS bag file to delete

        Returns:
            True if an entry was deleted, False otherwise
        """
        self.cursor.execute("DELETE FROM rosbags WHERE file_path = ?", (file_path,))
        deleted = self.cursor.rowcount > 0
        self.conn.commit()
        return deleted

    def get_database_stats(self) -> Dict[str, Any]:
        """Print statistics about the database."""
        self.cursor.execute("SELECT COUNT(*) FROM rosbags")
        rosbag_count = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM schema_modifications")
        total_columns = self.cursor.fetchone()[0]

        # TODO: return category counts like:
        # skidpad: 5
        # acceleration: 3

        # self.cursor.execute(
        #     "SELECT map_category, COUNT(*) FROM rosbags GROUP BY map_category"
        # )
        # category_counts = self.cursor.fetchall()

        return {
            "rosbag_count": rosbag_count,
            "total_columns": total_columns,
        }
