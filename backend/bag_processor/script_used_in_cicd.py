import os
import time
from typing import List

import requests


def make_api_request(
    headers,
    url,
    method="post",
    params=None,
    json_data=None,
    success_msg="Operation successful",
    error_msg="Operation failed",
):
    """Unified API request handler"""
    method = method.lower()

    if method == "post":
        response = requests.post(url, params=params, headers=headers, json=json_data)
    elif method == "delete":
        response = requests.delete(url, params=params, headers=headers, json=json_data)
    elif method == "get":
        response = requests.get(url, params=params, headers=headers)
    elif method == "put":
        response = requests.put(url, params=params, headers=headers, json=json_data)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")
    if response.status_code == 200:
        print(success_msg)
        return response.json(), True
    else:
        print(f"{error_msg}: ", response.json())
        raise Exception(error_msg)


def play_rosbag_and_wait(rosbag_path, backend_url, headers):
    """Play rosbag and wait for completion"""
    # Play rosbag
    _, _ = make_api_request(
        headers,
        f"{backend_url}/api/rosbags/play/start?bag_path={rosbag_path}",
        method="post",
        success_msg="Rosbag played successfully",
        error_msg="Error playing rosbag",
    )

    # Check rosbag status
    status_url = f"{backend_url}/api/rosbags/play/status"
    response = requests.post(status_url, headers=headers)

    while response.status_code == 200 and response.json().get("running") is True:
        time.sleep(5)
        print("Rosbag status: ", response.json())
        response = requests.post(status_url, headers=headers)

    if response.status_code == 200 and (
        response.json().get("running") is False or response.json().get("running") is None
    ):
        print("Rosbag status: ", response.json())

        # stop rosbag
        _, _ = make_api_request(
            headers,
            f"{backend_url}/api/rosbags/play/stop",
            method="post",
            success_msg="Rosbag stoped successfully",
            error_msg="Error stopping rosbag",
        )
        return response.json()
    else:
        print("Error checking rosbag status: ", response.json())
        raise Exception("Error checking rosbag status")


# Main program
def open_loop_test(
    rosbags_paths: List[str],
    image_tag: str,
):
    backend_url = "http://localhost:8080"
    headers = {"accept": "application/json"}

    for rosbag_path in rosbags_paths:
        if not os.path.exists(rosbag_path):
            raise FileNotFoundError(f"Rosbag file does not exist: {rosbag_path}")

    # Initialize container from image
    response, _ = make_api_request(
        headers,
        f"{backend_url}/api/docker/run",
        method="post",
        params={
            "image_tag": f"{image_tag}",
        },
        json_data={
            "name": "workspace",
            "network": "host",
            "command": [
                "/bin/bash",
                "-c",
                "source scripts/launch/launch_all_sim.bash && tail -f /dev/null",
            ],
        },
        success_msg="Container started successfully",
        error_msg="Error starting container",
    )

    # Print container ID after we have the data
    if response and "container_id" in response:
        container_id = response.get("container_id")
        print(f"Container ID: {container_id}")

    # Process all rosbags in sequence
    for i, rosbag_path in enumerate(rosbags_paths):
        print(f"Processing rosbag {i+1}/{len(rosbags_paths)}: {rosbag_path}")

        # Play rosbag and wait for completion
        play_rosbag_and_wait(rosbag_path, backend_url, headers)
        if i < len(rosbags_paths) - 1:
            # If not the last rosbag, stop and restart container for the next one
            _, _ = make_api_request(
                headers,
                f"{backend_url}/api/docker/stop/{container_id}",
                method="post",
                success_msg="Container stopped successfully",
                error_msg="Error stopping container",
            )

            _, _ = make_api_request(
                headers,
                f"{backend_url}/api/docker/run",
                method="post",
                params={
                    "container_id": f"{container_id}",
                },
                success_msg="Container restarted successfully",
                error_msg="Error restarting container",
            )

    # After all rosbags are processed, stop the container
    _, _ = make_api_request(
        headers,
        f"{backend_url}/api/docker/stop/{container_id}",
        method="post",
        success_msg="Container stopped successfully",
        error_msg="Error stopping container",
    )

    # Copy evaluation data from container to host
    _, _ = make_api_request(
        headers,
        f"{backend_url}/api/docker/copy/{container_id}",
        method="post",
        json_data={
            "source_path": "/home/vscode/workspace/src/lidar/evaluation/",
            "destination_path": "/tmp/output/lidar/",
        },
        success_msg="Data copied successfully",
        error_msg="Error copying data",
    )

    _, _ = make_api_request(
        headers,
        f"{backend_url}/api/docker/copy/{container_id}",
        method="post",
        json_data={
            "source_path": "/home/vscode/workspace/src/estimation/evaluation/",
            "destination_path": "/tmp/output/estimation/",
        },
        success_msg="Data copied successfully",
        error_msg="Error copying data",
    )

    # Remove container
    _, _ = make_api_request(
        headers,
        f"{backend_url}/api/docker/remove/{container_id}",
        method="delete",
        success_msg="Container deleted successfully",
        error_msg="Error deleting container",
    )
