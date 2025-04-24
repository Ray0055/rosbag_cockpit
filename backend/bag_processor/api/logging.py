import logging
import os
from enum import Enum


class LogType(str, Enum):
    SERVER = "server"
    DB = "db_service"
    DOCKER = "docker_service"
    BAG = "bag_player"
    TEST = "open_loop_test"


# 确保日志目录存在
log_dir = "bag_processor/api/logs"
os.makedirs(log_dir, exist_ok=True)

# 定义共享的格式化器
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")

# 基本配置（用于控制台输出或未指定的日志器）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# 创建和配置所有日志器
loggers = {
    "server": "server.log",
    "db_service": "db_service.log",
    "docker_service": "docker_service.log",
    "bag_player": "bag_player.log",
    "open_loop_test": "open_loop_test.log",
}

# 为每个日志器配置文件处理器
for logger_name, log_file in loggers.items():
    # 获取日志器
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    # 创建文件处理器
    file_handler = logging.FileHandler(os.path.join(log_dir, log_file), mode="a")
    file_handler.setFormatter(formatter)

    # 添加处理器到日志器
    logger.addHandler(file_handler)

    # 防止日志传播到根日志器（避免日志重复）
    logger.propagate = False

# 现在你可以获取这些日志器进行使用
server_logger = logging.getLogger("server")
dbService_logger = logging.getLogger("db_service")
docker_service_logger = logging.getLogger("docker_service")
bag_player_logger = logging.getLogger("bag_player")
open_loop_test_logger = logging.getLogger("open_loop_test")
