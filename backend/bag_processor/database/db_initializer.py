import os

from sqlalchemy import create_engine

from .schema import DatabaseSchema


class DBInitializer:
    """
    This class is responsible for initializing the database.
    It creates the necessary tables and indexes if they do not exist.
    """

    def __init__(self, db_path: str):
        """
        Initialize the DBInitializer.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path

    def db_exists(self) -> bool:
        """
        Check if the database file exists.

        Returns:
            bool: True if the database file exists, False otherwise
        """
        return os.path.exists(self.db_path)

    def initialize_db(self) -> None:
        """
        Initialize the database schema.
        This method should be called to create the necessary tables and indexes.
        """
        if self.db_exists():
            print(f"Database already exists at {self.db_path}. Initialization skipped.")
            return

        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
            print(f"Created directory for database: {db_dir}")

        engine = create_engine(f"sqlite:///{self.db_path}")
        with engine.connect() as connection:
            DatabaseSchema.initialize_database(connection)
            print("Database schema initialized successfully")
