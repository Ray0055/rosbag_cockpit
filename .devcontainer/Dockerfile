FROM python:3.8-alpine

RUN apk add --update --no-cache nodejs npm && \
    pip install uv 
RUN apk add --update --no-cache git && \
    rm -rf /var/cache/apk/*

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=1000

# Create user and group matching local user
RUN addgroup -g $USER_GID $USERNAME \
    && adduser -u $USER_UID -G $USERNAME -s /bin/sh -D $USERNAME