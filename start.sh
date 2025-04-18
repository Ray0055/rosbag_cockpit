#!/bin/bash
export DOCKER_GID=$(getent group docker | cut -d: -f3)
export USERNAME=$(whoami)
docker compose up -d
