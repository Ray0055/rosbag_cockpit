from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.pool import QueuePool


class DBConnectionPool:
    """Manages SQLAlchemy connection pool for database operations."""

    def __init__(
        self,
        db_url: str,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
    ):
        """
        Initialize connection pool for database.

        Args:
            db_url: Database URL in SQLAlchemy format (e.g., "sqlite:///database.db")
            pool_size: Number of connections to keep open in the pool
            max_overflow: Maximum number of connections to create beyond pool_size
            pool_timeout: Seconds to wait for a connection from the pool
            pool_recycle: Seconds after which a connection is recycled
        """
        connect_args = {}
        if db_url.startswith("sqlite"):
            # SQLite specific settings for concurrency
            connect_args["check_same_thread"] = False

        self.engine = create_engine(
            db_url,
            connect_args=connect_args,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
        )

    @contextmanager
    def get_connection(self) -> Generator[Connection, None, None]:
        """
        Get a database connection from the pool as a context manager.

        Yields:
            SQLAlchemy Connection that will be returned to the pool after use
        """
        connection = self.engine.connect()
        try:
            yield connection
        finally:
            connection.close()

    def get_db(self) -> Generator[Connection, None, None]:
        """
        Get a database connection for dependency injection.
        Ideal for FastAPI Depends() usage.

        Yields:
            SQLAlchemy Connection from the connection pool
        """
        connection = self.engine.connect()
        try:
            yield connection
        finally:
            connection.close()

    def get_engine(self) -> Engine:
        """
        Get the SQLAlchemy engine.

        Returns:
            SQLAlchemy Engine object
        """
        return self.engine

    def dispose(self) -> None:
        """
        Dispose of the connection pool.
        Should be called when shutting down the application.
        """
        self.engine.dispose()
