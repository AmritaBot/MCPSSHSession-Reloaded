# Build stage
FROM python:3.12-slim AS builder
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-editable

# Runtime stage
FROM python:3.12-slim
WORKDIR /app

RUN useradd -m -s /bin/bash mcpuser && \
    mkdir -p /mounts/ssh-keys /mounts/ssh-config /tmp/mcp_ssh_session_logs && \
    chown -R mcpuser:mcpuser /app /mounts /tmp/mcp_ssh_session_logs

COPY --from=builder /app/.venv .venv
COPY pyproject.toml .
COPY src/ src/

# Symlink SSH config & keys into mcpuser's home
RUN mkdir -p /home/mcpuser/.ssh && \
    ln -sf /mounts/ssh-keys /home/mcpuser/.ssh/keys && \
    [ -f /mounts/ssh-config/config ] && ln -sf /mounts/ssh-config/config /home/mcpuser/.ssh/config || true

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
ENV PATH="/app/.venv/bin:$PATH"
USER mcpuser

ENTRYPOINT ["mcp-ssh", "serve", "mcp"]
