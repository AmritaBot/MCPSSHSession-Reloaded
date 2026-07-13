"""Core API types for SSH session management.

Pure data layer — no dependencies on paramiko, fastmcp, or any I/O.
These types declare *what* you want to do, not *how* to do it.
"""

from dataclasses import dataclass, field
from enum import Enum, auto

from pydantic_settings import BaseSettings, SettingsConfigDict

#  Identity & connection


class DeviceFamily(Enum):
    """Broad device category — drives shell interaction strategy."""

    UNIX = auto()
    CISCO = auto()
    JUNIPER = auto()
    MIKROTIK = auto()
    FORTINET = auto()
    ARISTA = auto()
    PALOALTO = auto()
    CHECKPOINT = auto()
    VYOS = auto()
    OPENWRT = auto()
    GENERIC_NETWORK = auto()
    UNKNOWN = auto()


class AuthMethod(Enum):
    PASSWORD = auto()
    KEY = auto()
    AGENT = auto()
    NONE = auto()


@dataclass
class ConnectionParams:
    """Immutable-ish description of *how* to reach a host.

    This is the data you declare.  The service layer resolves
    SSH config / env overrides / key paths at execution time.
    """

    host: str
    port: int = 22
    username: str | None = None
    password: str | None = None
    key_filename: str | None = None
    device_family: DeviceFamily = DeviceFamily.UNKNOWN

    # Privilege elevation
    sudo_password: str | None = None
    enable_password: str | None = None
    enable_command: str = "enable"

    # Optional tags for grouping / filtering
    tags: list[str] = field(default_factory=list)

    @property
    def session_key(self) -> str:
        """Canonical session identifier."""
        u = self.username or "?"
        return f"{u}@{self.host}:{self.port}"

    def with_overrides(self, **kw) -> "ConnectionParams":
        """Return a copy with some fields replaced."""
        d = {f.name: getattr(self, f.name) for f in self.__dataclass_fields__.values()}  # type: ignore[arg-type]
        d.update(kw)
        return ConnectionParams(**d)


#  Execution results


class CommandStatus(Enum):
    RUNNING = "running"
    AWAITING_INPUT = "awaiting_input"
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"
    FAILED = "failed"


@dataclass
class CommandResult:
    """Outcome of a single command execution."""

    stdout: str
    stderr: str
    exit_code: int
    status: CommandStatus = CommandStatus.COMPLETED
    command_id: str | None = None
    duration_ms: float = 0.0
    truncated: bool = False


@dataclass
class FileContent:
    """Result of a remote file read."""

    content: str
    path: str
    truncated: bool = False
    max_bytes: int = 0


#  Session lifecycle


@dataclass
class SessionInfo:
    """Lightweight summary of an active session."""

    session_key: str
    host: str
    port: int
    username: str
    device_family: DeviceFamily = DeviceFamily.UNKNOWN
    connected_at: str = ""
    last_active: str = ""
    active_command: bool = False
    enable_mode: bool = False


@dataclass
class SessionDiagnostics:
    """Full diagnostics for one session."""

    session_key: str
    connection_health: str = "unknown"
    shell_type: str = "unknown"
    prompt_captured: str | None = None
    prompt_pattern: str | None = None
    prompt_confidence: float = 0.0
    last_activity: str = ""
    shell_state: dict = field(default_factory=dict)
    recent_commands: list[str] = field(default_factory=list)
    optimization_hints: list[str] = field(default_factory=list)


#  Server config


class ServerConfig(BaseSettings):
    """Tunables for the SSH service — read once at startup.

    Values are resolved in this priority (highest to lowest):
      1. Explicit constructor kwargs
      2. Environment variables (MCP_SSH_*)
      3. Class-level defaults

    Example::

        export MCP_SSH_DEFAULT_TIMEOUT=60
        export MCP_SSH_INTERACTIVE_MODE=false
    """

    model_config = SettingsConfigDict(
        env_prefix="MCP_SSH_",
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    default_timeout: int = 30
    max_timeout: int = 300
    connect_timeout: int = 30
    max_workers: int = 10
    max_file_bytes: int = 2 * 1024 * 1024
    max_output_bytes: int = 10 * 1024 * 1024
    interactive_mode: bool = True
    pty_aware_validation: bool = False
    mikrotik_auto_paging: bool = True
    terminal_width: int = 100
    terminal_height: int = 24
    log_dir: str = "/tmp/mcp_ssh_session_logs"
    background_monitor_max_timeout: int = 300
    normal_idle_timeout: int = 2
    package_manager_idle_timeout: int = 10
    async_default_timeout: int = 30


#  Error types


class ErrorCategory(Enum):
    NETWORK = "network"
    AUTH = "auth"
    TIMEOUT = "timeout"
    PERMISSION = "permission"
    COMMAND = "command"
    PROTOCOL = "protocol"
    UNKNOWN = "unknown"


class SSHError(Exception):
    """Structured error returned by the service layer."""

    category: ErrorCategory
    message: str
    detail: str
    hint: str
    recoverable: bool

    def __init__(
        self,
        category: ErrorCategory,
        message: str,
        *,
        detail: str = "",
        hint: str = "",
        recoverable: bool = False,
    ):
        self.category = category
        self.message = message
        self.detail = detail
        self.hint = hint
        self.recoverable = recoverable
        super().__init__(message)
