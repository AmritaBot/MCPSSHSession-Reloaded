# Safety Protections

Built-in mechanisms that keep the server responsive and prevent resource exhaustion.

## Command Execution

All commands run in background threads (`ThreadPoolExecutor`). If a synchronous
`execute()` exceeds its timeout, it auto-transitions to async mode and returns
a `command_id` — the server never hangs.

```python
from mcp_ssh_reloaded import SSHService, ConnectionParams, CommandStatus

svc = SSHService()
conn = ConnectionParams(host="myserver")

r = svc.execute(conn, "sleep 100", timeout=10)
if r.status == CommandStatus.RUNNING:
    while True:
        s = svc.get_command_status(r.command_id)
        if s["status"] != "running":
            break
```

## Completion Detection

Commands complete when **either** condition is met:

1. **Prompt detected** — captured shell prompt or regex matches tail of output
2. **Idle timeout** (2 s) — timer resets on every chunk; long builds keep running

## Output & File Limits

| Limit          | Value | Enforced by                          |
| -------------- | ----- | ------------------------------------ |
| Command stdout | 10 MB | `OutputLimiter`                      |
| File read      | 2 MB  | `FileManager` (SFTP / sudo fallback) |
| File write     | 2 MB  | `FileManager` (SFTP / sudo tee)      |

Truncation adds `[CONTENT TRUNCATED]` marker.

## Timeouts

| Timeout                | Default | Max   | Tunable via                                                          |
| ---------------------- | ------- | ----- | -------------------------------------------------------------------- |
| Command                | 30 s    | 300 s | `timeout` param / `MCP_SSH_DEFAULT_TIMEOUT` env var / `ServerConfig` |
| SSH connect            | 30 s    | —     | `MCP_SSH_CONNECT_TIMEOUT` / `ServerConfig.connect_timeout`           |
| Enable mode            | 10 s    | —     | internal                                                             |
| Normal idle            | 2 s     | —     | `MCP_SSH_NORMAL_IDLE_TIMEOUT`                                        |
| Package manager idle   | 10 s    | —     | `MCP_SSH_PACKAGE_MANAGER_IDLE_TIMEOUT`                               |
| Async default          | 30 s    | —     | `MCP_SSH_ASYNC_DEFAULT_TIMEOUT`                                      |
| Background monitor max | 300 s   | —     | `MCP_SSH_BACKGROUND_MONITOR_MAX_TIMEOUT`                             |

**All fields** can be set via `MCP_SSH_*` environment variables or `ServerConfig` constructor:

```bash
export MCP_SSH_DEFAULT_TIMEOUT=60
export MCP_SSH_CONNECT_TIMEOUT=15
export MCP_SSH_BACKGROUND_MONITOR_MAX_TIMEOUT=600
```

```python
from mcp_ssh_reloaded import ServerConfig
svc = SSHService(config=ServerConfig(default_timeout=60, max_timeout=600))
```

See [README](../README.md#configuration) for the full env var reference.

## Session Recovery

- Dead shells auto-detected and recreated on next command
- Stuck prompt: after 5 consecutive misses, Ctrl+C → recapture prompt
- `close_all()` cleans up shells, clients, thread pool

## Error Handling

Service errors raised as `SSHError(Exception)`:

| Field         | Description                                                                                    |
| ------------- | ---------------------------------------------------------------------------------------------- |
| `category`    | `ErrorCategory` (`NETWORK`, `AUTH`, `TIMEOUT`, `PERMISSION`, `COMMAND`, `PROTOCOL`, `UNKNOWN`) |
| `message`     | Human-readable summary                                                                         |
| `detail`      | Original error string                                                                          |
| `hint`        | Suggested fix                                                                                  |
| `recoverable` | Whether retrying may succeed                                                                   |

→ Full reference: [API-DOCS.md](../API-DOCS.md#error-handling)
