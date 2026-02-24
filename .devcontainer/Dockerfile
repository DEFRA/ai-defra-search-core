FROM mcr.microsoft.com/devcontainers/python:1-3.13-bookworm
USER root

# Remove broken Yarn apt repo (GPG key expired) - must run before any apt-get update
RUN rm -f /etc/apt/sources.list.d/yarn.list 2>/dev/null || true \
    && find /etc/apt/sources.list.d -name '*yarn*' -delete 2>/dev/null || true

USER vscode
