"""
Database schema definitions for the Cockpit application.

This module defines the SQLite table schemas and handles schema migrations.
"""

import sqlite3
from typing import List, Tuple, Dict, Any


class DatabaseSchema:
    """Manages the database schema creation and migrations."""
    
    # Initial schema definition for the rosbags table
    ROSBAGS_TABLE_SCHEMA = '''
    CREATE TABLE IF NOT EXISTS rosbags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT UNIQUE NOT NULL,
        map_category TEXT,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        duration REAL,
        size_mb REAL,
        message_count INTEGER,
        topic_count INTEGER,
        topics_json TEXT,
        metadata_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    '''
    
    # Schema for tracking modifications to the schema
    SCHEMA_MODIFICATIONS_TABLE = '''
    CREATE TABLE IF NOT EXISTS schema_modifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        column_name TEXT UNIQUE NOT NULL,
        data_type TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    '''
    
    # Initial columns for the rosbags table
    INITIAL_COLUMNS = [
        ("file_path", "TEXT"),
        ("map_category", "TEXT"),
        ("start_time", "TIMESTAMP"),
        ("end_time", "TIMESTAMP"),
        ("duration", "REAL"),
        ("size_mb", "REAL"),
        ("message_count", "INTEGER"),
        ("topic_count", "INTEGER"),
        ("topics_json", "TEXT"),
        ("metadata_json", "TEXT")
    ]
    
    @staticmethod
    def initialize_database(cursor: sqlite3.Cursor) -> None:
        """
        Initialize the database schema.
        
        Args:
            cursor: SQLite cursor object
        """
        # Create tables
        cursor.execute(DatabaseSchema.ROSBAGS_TABLE_SCHEMA)
        cursor.execute(DatabaseSchema.SCHEMA_MODIFICATIONS_TABLE)
        
        # Record initial columns
        for col_name, data_type in DatabaseSchema.INITIAL_COLUMNS:
            cursor.execute('''
            INSERT OR IGNORE INTO schema_modifications (column_name, data_type)
            VALUES (?, ?)
            ''', (col_name, data_type))
    
    @staticmethod
    def get_existing_columns(cursor: sqlite3.Cursor) -> List[str]:
        """
        Get a list of all existing column names in the rosbags table.
        
        Args:
            cursor: SQLite cursor object
            
        Returns:
            List of column names
        """
        cursor.execute("PRAGMA table_info(rosbags)")
        columns = [row[1] for row in cursor.fetchall()]
        return columns
    
    @staticmethod
    def add_column_if_not_exists(cursor: sqlite3.Cursor, column_name: str, data_type: str) -> bool:
        """
        Add a new column to the rosbags table if it doesn't already exist.
        
        Args:
            cursor: SQLite cursor object
            column_name: Name of the column to add
            data_type: SQLite data type for the column
            
        Returns:
            True if a new column was added, False otherwise
        """
        existing_columns = DatabaseSchema.get_existing_columns(cursor)
        
        if column_name not in existing_columns:
            # Add the column to the table
            sql = f"ALTER TABLE rosbags ADD COLUMN {column_name} {data_type}"
            cursor.execute(sql)
            
            # Record the modification
            cursor.execute('''
            INSERT OR IGNORE INTO schema_modifications (column_name, data_type)
            VALUES (?, ?)
            ''', (column_name, data_type))
            
            return True
        
        return False
    
    @staticmethod
    def determine_sqlite_type(value: Any) -> str:
        """
        Determine the appropriate SQLite data type based on a Python value.
        
        Args:
            value: Python value
            
        Returns:
            SQLite data type as a string
        """
        if isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "REAL"
        elif isinstance(value, bool):
            return "BOOLEAN"
        else:
            return "TEXT"