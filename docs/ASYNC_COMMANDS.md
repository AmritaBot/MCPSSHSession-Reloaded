# Async Commands

Long-running commands auto-transition to background execution — the server
never blocks.

## Quick Start

```python
from mcp_ssh_reloaded import SSHService, ConnectionParams, CommandStatus

svc = SSHService()
conn = ConnectionParams(host="myserver")

# Sync — returns output if done within timeout
r = svc.execute(conn, "uptime")
print(r.stdout)

# Auto async — exceeds timeout, returns RUNNING + command_id
r = svc.execute(conn, "sleep 100", timeout=5)
if r.status == CommandStatus.RUNNING:
    while True:
        s = svc.get_command_status(r.command_id)
        if s["status"] != "running":
            break
```

## Explicit Async

```python
cmd_id = svc.execute_async(conn, "long_backup.sh", timeout=600)
status = svc.get_command_status(cmd_id)
svc.send_input(cmd_id, "yes\n")  # respond to prompts
svc.interrupt(cmd_id)             # Ctrl+C
svc.list_running()                # all active
svc.list_history(limit=50)        # recent completed/failed
```

## Return Values

| Scenario          | `exit_code` | `status`         | How to proceed                    |
| ----------------- | ----------- | ---------------- | --------------------------------- |
| Completed in time | 0-255       | `COMPLETED`      | Read `.stdout`                    |
| Timed out → async | 0           | `RUNNING`        | Poll `get_command_status(cmd_id)` |
| Needs input       | 0           | `AWAITING_INPUT` | Use `send_input(cmd_id, text)`    |
| Error             | varies      | `FAILED`         | Check `.stderr`                   |

## MCP Client Timeouts

Claude and similar clients have HTTP timeouts (~60 s). The command keeps
running server-side. Recover with `list_running_commands()` +
`get_command_status()`.

**Tip:** Use `execute_command_async` directly for known-long operations to
avoid MCP timeouts entirely.
