FROM mcr.microsoft.com/devcontainers/python:1-3.13-bookworm
USER root

# Remove broken Yarn apt repo (GPG key expired) - must run before any apt-get update
RUN rm -f /etc/apt/sources.list.d/yarn.list 2>/dev/null || true \
    && find /etc/apt/sources.list.d -name '*yarn*' -delete 2>/dev/null || true

# Install Docker CLI + compose (uses host docker via socket mount)
RUN apt-get update \
    && apt-get install -y ca-certificates curl gnupg lsb-release \
    && install -m0755 -d /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc \
    && chmod a+r /etc/apt/keyrings/docker.asc \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian bookworm stable" > /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y docker-ce-cli docker-buildx-plugin docker-compose-plugin \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

USER vscode
