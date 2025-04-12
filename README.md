# install uv
pip3 install uv

# Create a virtual environment with access to system packages (including ROS packages)
uv venv --system-site-packages

# Activate the virtual environment
source .venv/bin/activate

# Install the project
uv pip install -e .

## use vscode to launch project
add following to `launch.json`
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Main Script",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            "justMyCode": true,
            "cwd": "${workspaceFolder}",
            "args": []
        }
    ]
}
```
