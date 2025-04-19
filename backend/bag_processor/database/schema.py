from typing import Any, List

from sqlalchemy import Column, DateTime, Float, Integer, MetaData, Table, Text, inspect, text
from sqlalchemy.engine import Connection


class DatabaseSchema:
    """Manages the database schema for the Cockpit application."""

    @staticmethod
    def initialize_database(conn: Connection) -> None:
        """Initialize the database schema using SQLAlchemy."""
        metadata = MetaData()

        # Define the rosbags table if it doesn't exist
        if not inspect(conn).has_table("rosbags"):
            Table(
                "rosbags",
                metadata,
                Column("id", Integer, primary_key=True),
                Column("file_path", Text, unique=True, nullable=False),
                Column("file_name", Text),
                Column("file_type", Text),
                Column("map_category", Text),
                Column("size_mb", Float),
                Column("start_time", Text),
                Column("end_time", Text),
                Column("duration", Float),
                Column("message_count", Integer),
                Column("topic_count", Integer),
                Column("topics_json", Text),
                Column("metadata_json", Text),
                Column("created_at", DateTime, server_default="CURRENT_TIMESTAMP"),
            )

            # Create the table
            metadata.create_all(conn)

    @staticmethod
    def determine_sqlite_type(value: Any) -> str:
        """
        Determine the appropriate SQLite type for a given value.

        Args:
            value: Value to determine type for

        Returns:
            SQLite data type as string
        """
        if isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "REAL"
        elif isinstance(value, (list, dict)):
            return "TEXT"  # JSON will be stored as text
        else:
            return "TEXT"

    @staticmethod
    def add_column_if_not_exists(
        conn: Connection, column_name: str, data_type: str = "TEXT"
    ) -> bool:
        """
        Add a new column to the rosbags table if it doesn't already exist using SQLAlchemy.

        Args:
            conn: SQLAlchemy connection
            column_name: Name of the column to add
            data_type: SQLite data type for the column

        Returns:
            True if a new column was added, False if it already existed
        """
        insp = inspect(conn)

        # First check if the table exists
        if not insp.has_table("rosbags"):
            # Initialize the database if the table doesn't exist
            DatabaseSchema.initialize_database(conn)

        # Get existing columns
        columns = [column["name"] for column in insp.get_columns("rosbags")]

        # Add column if it doesn't exist
        if column_name not in columns:
            conn.execute(text(f"ALTER TABLE rosbags ADD COLUMN {column_name} {data_type}"))
            return True
        return False

    @staticmethod
    def get_existing_columns(conn: Connection) -> List[str]:
        """
        Get the list of existing columns in the rosbags table using SQLAlchemy.

        Args:
            conn: SQLAlchemy connection

        Returns:
            List of column names
        """
        insp = inspect(conn)
        return [column["name"] for column in insp.get_columns("rosbags")]
