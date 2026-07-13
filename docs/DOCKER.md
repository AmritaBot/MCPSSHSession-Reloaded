# Docker Usage for MCP SSH Session Server

This document explains how to run the MCP SSH Session server in Docker containers.

## Quick Start

### 1. Build the Image

```bash
docker build -t mcp-ssh-reloaded .
```

### 2. Run the Container

```bash
docker run --rm -i mcp-ssh-reloaded
```

## SSH Configuration

The container supports mounting SSH configuration and keys through dedicated mount points.

### Option 1: Mount Individual Files

```bash
docker run --rm -i \
  -v ~/.ssh/config:/mounts/ssh-config/config:ro \
  -v ~/.ssh/id_rsa:/mounts/ssh-keys/id_rsa:ro \
  -v ~/.ssh/id_rsa.pub:/mounts/ssh-keys/id_rsa.pub:ro \
  mcp-ssh-reloaded
```

### Option 2: Mount Entire SSH Directory

```bash
docker run --rm -i \
  -v ~/.ssh:/mounts/ssh-keys:ro \
  mcp-ssh-reloaded
```

### Option 3: Using Docker Compose

```bash
# Edit docker-compose.yml to uncomment the volume mounts
docker-compose up mcp-ssh-reloaded
```

## Mount Points

| Mount Point                 | Description                   | Required |
| --------------------------- | ----------------------------- | -------- |
| `/mounts/ssh-config/config` | SSH configuration file        | No       |
| `/mounts/ssh-keys/`         | Directory containing SSH keys | No       |

## Security Considerations

1. **Read-Only Mounts**: Always mount SSH files as read-only (`:ro`)
2. **Minimal Keys**: Only mount the keys you actually need
3. **Non-Root User**: Container runs as non-root user `mcpuser`
4. **File Permissions**: Container sets proper SSH file permissions automatically

## Environment Variables

| Variable                  | Default | Description                             |
| ------------------------- | ------- | --------------------------------------- |
| `PYTHONUNBUFFERED`        | `1`     | Ensures Python output is not buffered   |
| `PYTHONDONTWRITEBYTECODE` | `1`     | Prevents Python from writing .pyc files |

### Server configuration (`MCP_SSH_*`)

All `ServerConfig` fields can be set via environment variables. Key examples:

| Variable                                 | Default                     | Description                    |
| ---------------------------------------- | --------------------------- | ------------------------------ |
| `MCP_SSH_DEFAULT_TIMEOUT`                | `30`                        | Command timeout (seconds)      |
| `MCP_SSH_MAX_TIMEOUT`                    | `300`                       | Hard cap on timeout            |
| `MCP_SSH_CONNECT_TIMEOUT`                | `30`                        | SSH connect timeout            |
| `MCP_SSH_MAX_WORKERS`                    | `10`                        | Thread pool max workers        |
| `MCP_SSH_MAX_FILE_BYTES`                 | `2097152`                   | Max file read/write (2 MB)     |
| `MCP_SSH_MAX_OUTPUT_BYTES`               | `10485760`                  | Max command output (10 MB)     |
| `MCP_SSH_INTERACTIVE_MODE`               | `true`                      | Enable PTY terminal emulation  |
| `MCP_SSH_LOG_DIR`                        | `/tmp/mcp_ssh_session_logs` | Log directory                  |
| `MCP_SSH_NORMAL_IDLE_TIMEOUT`            | `2`                         | Normal idle timeout (seconds)  |
| `MCP_SSH_PACKAGE_MANAGER_IDLE_TIMEOUT`   | `10`                        | Package manager idle timeout   |
| `MCP_SSH_ASYNC_DEFAULT_TIMEOUT`          | `30`                        | Async command default timeout  |
| `MCP_SSH_BACKGROUND_MONITOR_MAX_TIMEOUT` | `300`                       | Background monitor max timeout |

See [README](../README.md#configuration) for the complete reference.

## Examples

### Basic Usage with SSH Keys

```bash
docker run --rm -i \
  -v ~/.ssh/id_rsa:/mounts/ssh-keys/id_rsa:ro \
  -v ~/.ssh/id_rsa.pub:/mounts/ssh-keys/id_rsa.pub:ro \
  mcp-ssh-reloaded
```

### With Custom SSH Config

```bash
docker run --rm -i \
  -v ./ssh-config:/mounts/ssh-config/config:ro \
  -v ~/.ssh:/mounts/ssh-keys:ro \
  mcp-ssh-reloaded
```

### With Persistent Logs

```bash
mkdir -p ./logs
docker run --rm -i \
  -v ~/.ssh:/mounts/ssh-keys:ro \
  -v ./logs:/tmp/mcp_ssh_session_logs \
  mcp-ssh-reloaded
```

### Development Mode

```bash
docker run --rm -i \
  -v ~/.ssh:/mounts/ssh-keys:ro \
  -v $(pwd):/app \
  -w /app \
  mcp-ssh-reloaded uv run mcp-ssh
```

## Docker Compose Examples

### Basic Setup

```yaml
version: "3.8"
services:
  mcp-ssh-reloaded:
    build: .
    stdin_open: true
    volumes:
      - ~/.ssh:/mounts/ssh-keys:ro
```

### Production Setup

```yaml
version: "3.8"
services:
  mcp-ssh-reloaded:
    build: .
    stdin_open: true
    restart: unless-stopped
    volumes:
      - ~/.ssh/config:/mounts/ssh-config/config:ro
      - ~/.ssh:/mounts/ssh-keys:ro
      - ./logs:/tmp/mcp_ssh_session_logs
    environment:
      - PYTHONUNBUFFERED=1
      - PYTHONDONTWRITEBYTECODE=1
      - MCP_SSH_DEFAULT_TIMEOUT=60
      - MCP_SSH_MAX_WORKERS=20
```

### With Custom Timeouts

```bash
docker run --rm -i \
  -v ~/.ssh:/mounts/ssh-keys:ro \
  -e MCP_SSH_DEFAULT_TIMEOUT=60 \
  -e MCP_SSH_CONNECT_TIMEOUT=15 \
  mcp-ssh-reloaded
```

## Troubleshooting

### SSH Key Permissions

The container automatically sets correct permissions for SSH files:

- Private keys: `600` (read/write by owner only)
- Public keys: `644` (readable by all)
- SSH config: `600`
- `.ssh` directory: `700`

### Debug Mode

Run with verbose output:

```bash
docker run --rm -i \
  -v ~/.ssh:/mounts/ssh-keys:ro \
  -e DEBUG=1 \
  mcp-ssh-reloaded
```

### Check SSH Setup

Enter the container to verify SSH configuration:

```bash
docker run --rm -it \
  -v ~/.ssh:/mounts/ssh-keys:ro \
  --entrypoint /bin/bash \
  mcp-ssh-reloaded

# Inside container:
ls -la /home/mcpuser/.ssh/
ssh -T git@github.com  # Test SSH connection
```

## Building and Publishing

### Build for Different Platforms

```bash
# Build for current platform
docker build -t mcp-ssh-reloaded .

# Build for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64 -t mcp-ssh-reloaded .
```

### Tag and Push

```bash
docker tag mcp-ssh-reloaded:latest your-registry/mcp-ssh-reloaded:latest
docker push your-registry/mcp-ssh-reloaded:latest
```

## Integration with MCP Clients

The container communicates via stdio, so it can be used with any MCP client:

```bash
# Example with Claude Desktop
docker run --rm -i \
  -v ~/.ssh:/mounts/ssh-keys:ro \
  mcp-ssh-reloaded | claude-desktop
```

## Health Checks

The container includes a health check that verifies the MCP server process is running:

```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

## Logs

Application logs are written to `/tmp/mcp_ssh_session_logs/mcp_ssh_session.log` inside the container. Mount this directory to persist logs:

```bash
docker run --rm -i \
  -v ~/.ssh:/mounts/ssh-keys:ro \
  -v ./logs:/tmp/mcp_ssh_session_logs \
  mcp-ssh-reloaded
```
