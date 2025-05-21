import logging
import os
from enum import Enum


class LogType(str, Enum):
    SERVER = "server"
    DB = "db_service"
    DOCKER = "docker_service"
    BAG = "bag_player"
    TEST = "open_loop_test"


# Ensure the log directory exists
log_dir = "bag_processor/api/logs"
os.makedirs(log_dir, exist_ok=True)

# Define shared formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")

# Basic configuration (for console output or unspecified loggers)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Create and configure all loggers
loggers = {
    "server": "server.log",
    "db_service": "db_service.log",
    "docker_service": "docker_service.log",
    "bag_player": "bag_player.log",
    "open_loop_test": "open_loop_test.log",
}

# Configure file handlers for each logger
for logger_name, log_file in loggers.items():
    # Get logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    # Create file handler
    file_handler = logging.FileHandler(os.path.join(log_dir, log_file), mode="a")
    file_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(file_handler)

    # Prevent log propagation to root logger (avoid duplicate logs)
    logger.propagate = False

# Now you can get these loggers for use
server_logger = logging.getLogger("server")
dbService_logger = logging.getLogger("db_service")
docker_service_logger = logging.getLogger("docker_service")
bag_player_logger = logging.getLogger("bag_player")
open_loop_test_logger = logging.getLogger("open_loop_test")
