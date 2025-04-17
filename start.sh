#!/bin/bash
export DOCKER_GID=$(getent group docker | cut -d: -f3)
export DATABASE_PATH='/media/carmaker/Backup/00rosbag_datasets/rosbag_metadata.db'
docker compose up -d
