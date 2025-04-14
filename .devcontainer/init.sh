#!/bin/sh
set -e

# 设置项目环境
cd /home/vscode/
uv venv

cd /home/vscode/rosbag_cockpit/backend 
source /home/vscode/.venv/bin/activate 
uv pip install -e .

cd /home/vscode/rosbag_cockpit/frontend
npm install 