FROM node:16-alpine

ARG USERNAME=vscode
ARG USER_UID=1001
ARG USER_GID=1001

# Create user and group matching local user
RUN addgroup -g $USER_GID $USERNAME \
    && adduser -u $USER_UID -G $USERNAME -s /bin/sh -D $USERNAME


COPY . /home/vscode/rosbag_cockpit
RUN chown -R $USERNAME:$(getent group $USER_GID | cut -d: -f1) /home/vscode

WORKDIR /home/vscode/rosbag_cockpit/frontend

ENV NPM_CONFIG_REGISTRY=https://registry.npmjs.org/
ENV NPM_CONFIG_ALWAYS_AUTH=false

ENV HOME=/home/vscode

# Install dependencies using npm ci instead of npm install\
USER $USERNAME

RUN npm install
RUN npm run build -- --mode production

CMD ["npx", "serve", "-s", "dist", "-l", "5173"]
