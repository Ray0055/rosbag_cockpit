# use comm_pkg as base image to provide ros2 and customized msg
FROM comm_pkg:latest

RUN apt-get update && \
    apt-get install -y git python3-pip python3-tk && \
    pip3 install uv && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    "numpy>=1.24.4"  \
    pandas \
    matplotlib \
    ipykernel \
    papermill

ARG USERNAME=carmaker
ARG USER_UID=1000
ARG USER_GID=1000

# Create user and group matching local user
RUN groupadd -g $USER_GID $USERNAME \
    && useradd -u $USER_UID -g $USERNAME -s /bin/bash -m $USERNAME

RUN echo "source /opt/ros/galactic/setup.bash" >> /home/$USERNAME/.bashrc && \
echo "source /workspace/install/setup.bash" >> /home/$USERNAME/.bashrc

COPY . /home/$USERNAME/rosbag_cockpit/backend
RUN chown -R $USERNAME:$USERNAME /home/$USERNAME

WORKDIR /home/$USERNAME/rosbag_cockpit/backend

ENV HOME=/home/$USERNAME
USER $USERNAME
# Create a virtual environment and install dependencies
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install -e .

# Start the backend server
CMD . .venv/bin/activate && \
    uvicorn bag_processor.api:app --host 0.0.0.0 --port 8000 --reload --log-level info
