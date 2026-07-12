# MCP SSH Session

An MCP (Model Context Protocol) server that enables AI agents to establish and manage persistent SSH sessions.

## Features

- **Smart Command Execution** — auto-transitions to async mode if timeout is reached
- **Persistent Sessions** — SSH connections reused across commands
- **Async Commands** — non-blocking execution for long-running tasks
- **SSH Config Support** — reads `~/.ssh/config` for aliases, ports, keys
- **Multi-host** — manage connections to multiple hosts simultaneously
- **Network Devices** — enable mode handling for Cisco, Juniper, MikroTik, etc.
- **Sudo Support** — automatic password handling for Unix/Linux hosts
- **File Operations** — read/write remote files via SFTP (sudo fallback)
- **Command Interruption** — send Ctrl+C to stop running commands
- **Thread-safe** — safe for concurrent operations

## Quick Start

### Install

```bash
uvx mcp-ssh-reloaded
```

### Development

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

### CLI

```bash
# MCP server (default)
mcp-ssh-reloaded serve mcp

# Direct execution (no MCP)
mcp-ssh-reloaded exec myserver "uname -a" -u admin

# List / close sessions
mcp-ssh-reloaded list
mcp-ssh-reloaded close-all
```

### MCP Client Config

**Claude Code / Desktop** (`~/.claude.json` or `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "ssh-session": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-ssh-reloaded", "serve", "mcp"],
      "env": {}
    }
  }
}
```

### Quick Examples

```json
// SSH config alias
{ "host": "myserver", "command": "uptime" }

// Explicit params
{ "host": "example.com", "username": "user", "command": "ls -la", "port": 2222 }

// Network device (Cisco enable mode)
{ "host": "router", "username": "admin", "enable_password": "secret", "command": "show run" }

// Unix with sudo
{ "host": "server", "username": "ops", "sudo_password": "secret", "command": "systemctl restart nginx" }
```

---

> **Full API reference:** [API-DOCS.md](./API-DOCS.md) — all types, all methods, all MCP tools, error handling, server config tunables.

## SSH Config

`~/.ssh/config` is read automatically:

```
Host myserver
    HostName example.com
    User myuser
    Port 2222
    IdentityFile ~/.ssh/id_rsa
```

Then use `"host": "myserver"` — the rest is resolved for you.

## Credential Hiding (OVRD\_\*)

For production environments, store real credentials in env vars so AI agents only see aliases:

| Variable                   | Description             |
| -------------------------- | ----------------------- |
| `OVRD_{alias}_HOST`        | Real hostname or IP     |
| `OVRD_{alias}_PORT`        | SSH port                |
| `OVRD_{alias}_USER`        | SSH username            |
| `OVRD_{alias}_PASS`        | SSH password            |
| `OVRD_{alias}_KEY`         | Path to SSH private key |
| `OVRD_{alias}_SUDO_PASS`   | Sudo password           |
| `OVRD_{alias}_ENABLE_PASS` | Enable password         |

**Example config:**

```json
{
  "mcpServers": {
    "ssh-session": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-ssh-reloaded", "serve", "mcp"],
      "env": {
        "OVRD_prod_db_HOST": "192.168.1.100",
        "OVRD_prod_db_USER": "admin",
        "OVRD_prod_db_PASS": "secret123",
        "OVRD_prod_db_SUDO_PASS": "sudopass"
      }
    }
  }
}
```

The agent uses `"host": "prod_db"` — never sees real IPs or passwords.

## How It Works

Commands run inside persistent interactive shells:

- **Directory persists**: `cd /tmp` stays in `/tmp` for the next command
- **Env vars persist**: `export FOO=bar` is visible across commands
- **Prompt detection**: completion detected via captured prompt or idle timeout (2 s)
- **Session recovery**: stuck shells auto-reset after repeated prompt-detection failures

## Docs

| Doc                                                  | Topic                                                                  |
| ---------------------------------------------------- | ---------------------------------------------------------------------- |
| [API-DOCS.md](./API-DOCS.md)                         | Full API reference — types, SSHService methods, MCP tools, error model |
| [docs/ASYNC_COMMANDS.md](./docs/ASYNC_COMMANDS.md)   | Smart execution & async command lifecycle                              |
| [docs/INTERACTIVE_PTY.md](./docs/INTERACTIVE_PTY.md) | Terminal emulation mode                                                |
| [docs/DOCKER.md](./docs/DOCKER.md)                   | Running via Docker                                                     |

## License

MIT — see [LICENSE](./LICENSE).

## Fork

Fork of [devnullvoid/mcp-ssh-session](https://github.com/devnullvoid/mcp-ssh-session) with significant refactoring by [AmritaConstant](https://github.com/AmritaBot).
