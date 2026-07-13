"""Data structures for SSH session management."""

from __future__ import annotations

import threading
from concurrent.futures import Future
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import paramiko


class CommandStatus(Enum):
    RUNNING = "running"
    AWAITING_INPUT = "awaiting_input"  # Waiting for user input (password, prompt, etc.)
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"
    FAILED = "failed"
    STREAMING = "streaming"  # New: For long-running commands with streaming output


class ErrorCategory(Enum):
    """Categories of errors for better user understanding."""

    NETWORK = "network"
    AUTHENTICATION = "authentication"
    TIMEOUT = "timeout"
    COMMAND = "command"
    PROTOCOL = "protocol"
    PERMISSION = "permission"
    UNKNOWN = "unknown"


@dataclass
class ErrorInfo:
    """Structured error information with troubleshooting hints."""

    category: ErrorCategory
    message: str
    original_error: str | None = None
    troubleshooting_hint: str | None = None
    suggest_action: str | None = None


@dataclass
class SessionDiagnostics:
    """Diagnostic information about an SSH session."""

    session_key: str
    shell_type: str | None = None
    captured_prompt: str | None = None
    generalized_prompt: str | None = None
    prompt_pattern: str | None = None
    last_activity: datetime | None = None
    command_history: list[str] = field(default_factory=list)
    prompt_detection_confidence: float = 0.0
    shell_state: dict[str, Any] = field(default_factory=dict)
    connection_health: str = "unknown"  # "healthy", "degraded", "dead"


@dataclass
class RunningCommand:
    command_id: str
    session_key: str
    command: str
    shell: paramiko.Channel
    future: Future[Any] | None
    status: CommandStatus
    stdout: str
    stderr: str
    exit_code: int | None
    start_time: datetime
    end_time: datetime | None
    awaiting_input_reason: str | None = (
        None  # What is the command waiting for? (e.g., "password", "user_input")
    )
    monitoring_cancelled: threading.Event = field(default_factory=threading.Event)
    sentinel: str | None = None  # Sentinel marker used for Unix command completion

    # New fields for enhanced UX
    auto_extend_timeout: bool = False
    max_timeout: int = 300  # Maximum timeout if auto-extending
    progress_callback: str | None = None  # MCP tool name for progress callbacks
    streaming_mode: bool = False
    last_output_time: datetime | None = None
    output_chunks: list[str] = field(default_factory=list)  # For streaming mode


@dataclass
class ConnectionProfile:
    """Cached SSH connection profile for performance."""

    hostname: str
    username: str
    port: int
    key_filename: str | None
    config_host: str | None  # Original SSH config alias
    resolved_at: datetime = field(default_factory=datetime.now)

    # Performance metrics
    connect_count: int = 0
    last_connect: datetime | None = None
    avg_connect_time: float = 0.0
    connection_health: str = "unknown"  # "healthy", "degraded", "dead"
