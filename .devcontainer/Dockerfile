FROM python:3.8-alpine

RUN apk add --update --no-cache nodejs npm && \
    pip install uv 

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=1000

# 创建与本地用户匹配的用户和组
RUN addgroup -g $USER_GID $USERNAME \
    && adduser -u $USER_UID -G $USERNAME -s /bin/sh -D $USERNAME