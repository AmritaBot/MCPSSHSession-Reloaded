"""Enhanced MCP server with additional diagnostic and UX tools."""

from fastmcp import FastMCP

from .error_handler import ErrorHandler
from .logging_manager import get_logger
from .session_manager import SSHSessionManager

# Initialize enhanced MCP server
mcp = FastMCP("ssh-session-enhanced")
session_manager = SSHSessionManager()
logger = get_logger("enhanced_server")


@mcp.tool()
def execute_command_enhanced(
    host: str,
    command: str,
    username: str | None = None,
    password: str | None = None,
    key_filename: str | None = None,
    port: int | None = None,
    enable_password: str | None = None,
    enable_command: str = "enable",
    sudo_password: str | None = None,
    timeout: int = 30,
    auto_extend_timeout: bool = True,
    max_timeout: int = 600,
    streaming_mode: bool = False,
    progress_callback: str | None = None,
) -> str:
    """Execute a command with enhanced features for better UX.

    This tool provides advanced features for long-running commands and improved
    error handling with automatic troubleshooting suggestions.

    Enhanced Features:
    - auto_extend_timeout: Automatically extends timeout for long-running commands
    - streaming_mode: Returns output as it streams (ideal for very long operations)
    - progress_callback: Provides progress updates during execution

    The host parameter can be either a hostname/IP or an SSH config alias.

    Args:
        host: Hostname, IP address, or SSH config alias
        command: Command to execute
        username: SSH username (optional, will use SSH config)
        password: Password (optional)
        key_filename: Path to SSH key file (optional, will use SSH config)
        port: SSH port (optional, will use SSH config or default 22)
        enable_password: Enable mode password for network devices (optional)
        enable_command: Command to enter enable mode (default: "enable")
        sudo_password: Password for sudo commands on Unix/Linux hosts (optional)
        timeout: Initial timeout in seconds (default: 30)
        auto_extend_timeout: Automatically extend timeout for long operations (default: True)
        max_timeout: Maximum timeout when auto-extending (default: 600)
        streaming_mode: Return output as it streams (default: False)
        progress_callback: Tool name for progress callbacks (optional)

    Returns:
        Command output or enhanced status information with progress updates
    """
    logger.info(f"Enhanced command execution: {command[:50]}... on {host}")

    try:
        result = session_manager.execute_command_enhanced(
            host=host,
            username=username,
            command=command,
            password=password,
            key_filename=key_filename,
            port=port,
            enable_password=enable_password,
            enable_command=enable_command,
            sudo_password=sudo_password,
            timeout=timeout,
            auto_extend_timeout=auto_extend_timeout,
            max_timeout=max_timeout,
            streaming_mode=streaming_mode,
            progress_callback=progress_callback,
        )

        logger.info("Enhanced command completed successfully")
        return result

    except Exception as e:
        error_info = ErrorHandler.categorize_error(str(e), e)
        logger.error(f"Enhanced command failed: {error_info.message}")
        return ErrorHandler.format_error_for_ai(error_info)


@mcp.tool()
def get_session_diagnostics(
    host: str, username: str | None = None, port: int | None = None
) -> str:
    """Get comprehensive diagnostics for an SSH session.

    Provides detailed information about session health, shell state, prompt detection,
    and performance metrics for troubleshooting and optimization.

    Args:
        host: Hostname, IP address, or SSH config alias
        username: SSH username (optional, will use SSH config)
        port: SSH port (optional, will use SSH config or default 22)

    Returns:
        Comprehensive diagnostic report with optimization suggestions
    """
    logger.info(f"Getting session diagnostics for {host}")

    try:
        diagnostics = session_manager.get_session_diagnostics(host, username, port)

        # Format diagnostic report
        report_parts = [
            f"🔍 Session Diagnostics for {diagnostics.session_key}",
            "",
            f"📊 Connection Health: {diagnostics.connection_health}",
            f"🖥️  Shell Type: {diagnostics.shell_type or 'unknown'}",
            f"🎯 Prompt Detection Confidence: {diagnostics.prompt_detection_confidence:.1f}%",
            "",
            "📝 Prompts:",
            f"  Captured: {repr(diagnostics.captured_prompt) if diagnostics.captured_prompt else 'None'}",
            f"  Generalized: {repr(diagnostics.generalized_prompt) if diagnostics.generalized_prompt else 'None'}",
            f"  Pattern: {diagnostics.prompt_pattern or 'None'}",
        ]

        if diagnostics.last_activity:
            report_parts.extend(
                [
                    "",
                    f"⏰ Last Activity: {diagnostics.last_activity.strftime('%Y-%m-%d %H:%M:%S')}",
                ]
            )

        if diagnostics.command_history:
            report_parts.extend(
                [
                    "",
                    "📚 Recent Commands:",
                    *[f"  - {cmd}" for cmd in diagnostics.command_history[-5:]],
                ]
            )

        # Shell state info
        if diagnostics.shell_state:
            report_parts.extend(
                [
                    "",
                    "⚙️  Shell State:",
                    *[
                        f"  {key}: {value}"
                        for key, value in diagnostics.shell_state.items()
                    ],
                ]
            )

        # Optimization suggestions
        suggestions = session_manager.session_diagnostics.suggest_session_optimization(
            diagnostics.session_key
        )
        if suggestions:
            report_parts.extend(
                [
                    "",
                    "💡 Optimization Suggestions:",
                    *[f"  • {suggestion}" for suggestion in suggestions],
                ]
            )

        return "\n".join(report_parts)

    except Exception as e:
        error_info = ErrorHandler.categorize_error(str(e), e)
        logger.error(f"Diagnostics failed: {error_info.message}")
        return ErrorHandler.format_error_for_ai(error_info)


@mcp.tool()
def reset_session_prompt(
    host: str, username: str | None = None, port: int | None = None
) -> str:
    """Reset and recapture prompt detection for a session.

    Useful when prompt detection is failing or behaving incorrectly.
    This will clear existing prompt data and recapture the current prompt.

    Args:
        host: Hostname, IP address, or SSH config alias
        username: SSH username (optional, will use SSH config)
        port: SSH port (optional, will use SSH config or default 22)

    Returns:
        Status of prompt reset operation
    """
    logger.info(f"Resetting session prompt for {host}")

    try:
        success = session_manager.reset_session_prompt(host, username, port)

        if success:
            return (
                f"✅ Successfully reset prompt detection for {host}\n"
                "Prompt detection has been cleared and recaptured.\n"
                "Command execution should now work normally."
            )
        else:
            return (
                f"❌ Failed to reset prompt detection for {host}\n"
                "The session may not have an active shell.\n"
                "Try executing a simple command to initialize the shell first."
            )

    except Exception as e:
        error_info = ErrorHandler.categorize_error(str(e), e)
        logger.error(f"Prompt reset failed: {error_info.message}")
        return ErrorHandler.format_error_for_ai(error_info)


@mcp.tool()
def get_connection_health_report() -> str:
    """Get health report for all active SSH connections.

    Provides an overview of all active sessions, their health status,
    and any connections that may need attention.

    Returns:
        Comprehensive connection health report with statistics
    """
    logger.info("Generating connection health report")

    try:
        report = session_manager.get_connection_health_report()

        report_parts = [
            "🌐 Connection Health Report",
            f"📅 Generated: {report['timestamp']}",
            "",
            "📊 Summary:",
            f"  Total Sessions: {report['total_sessions']}",
            f"  ✅ Healthy: {report['healthy_sessions']}",
            f"  ⚠️  Degraded: {report['degraded_sessions']}",
            f"  ❌ Dead: {report['dead_sessions']}",
            "",
            "🔍 Session Details:",
        ]

        for session_key, details in report["session_details"].items():
            health_emoji = {
                "healthy": "✅",
                "degraded": "⚠️",
                "dead": "❌",
                "error": "🚨",
            }.get(details["health"], "❓")

            report_parts.extend(
                [
                    f"\n  {health_emoji} {session_key}",
                    f"    Health: {details['health']}",
                    f"    Shell Type: {details['shell_type']}",
                    f"    Active Command: {'Yes' if details['has_active_command'] else 'No'}",
                    f"    Enable Mode: {'Yes' if details['enable_mode'] else 'No'}",
                ]
            )

            if "error" in details:
                report_parts.append(f"    Error: {details['error']}")

        # Performance metrics
        perf_metrics = session_manager.get_performance_metrics()
        if perf_metrics:
            report_parts.extend(
                [
                    "\n\n📈 Performance Metrics:",
                    *[
                        f"  {op}: {metrics['count']} calls, avg {metrics['avg_time']:.3f}s"
                        for op, metrics in perf_metrics.items()
                    ],
                ]
            )

        return "\n".join(report_parts)

    except Exception as e:
        error_info = ErrorHandler.categorize_error(str(e), e)
        logger.error(f"Health report failed: {error_info.message}")
        return ErrorHandler.format_error_for_ai(error_info)


@mcp.tool()
def get_command_status_enhanced(command_id: str) -> str:
    """Get enhanced status of a running command.

    Provides detailed status information including progress, timeout behavior,
    and streaming mode status for better command monitoring.

    Args:
        command_id: ID of the command to check

    Returns:
        Enhanced command status with detailed metrics
    """
    logger.info(f"Getting enhanced status for command {command_id}")

    try:
        status = session_manager.enhanced_executor.get_command_status_enhanced(
            command_id
        )

        if status["status"] == "not_found":
            return f"❌ Command {command_id} not found in active or recent commands"

        # Format enhanced status report
        status_emoji = {
            "running": "🔄",
            "completed": "✅",
            "failed": "❌",
            "interrupted": "⏹️",
            "awaiting_input": "⏸️",
        }.get(status["status"], "❓")

        report_parts = [
            f"{status_emoji} Enhanced Command Status: {command_id}",
            f"📊 Status: {status['status'].title()}",
            f"🕐 Start Time: {status['start_time']}",
        ]

        if "end_time" in status:
            report_parts.append(f"🏁 End Time: {status['end_time']}")

        if "duration_seconds" in status:
            duration = status["duration_seconds"]
            report_parts.append(f"⏱️  Duration: {duration:.1f}s")

        if "exit_code" in status:
            report_parts.append(f"🔢 Exit Code: {status['exit_code']}")

        # Enhanced features status
        if status["auto_extend_timeout"]:
            report_parts.append(
                f"🔄 Auto-Extend: Enabled (max: {status['max_timeout']}s)"
            )

        if status["streaming_mode"]:
            report_parts.append("📡 Streaming Mode: Active")

        if status["has_progress_callback"]:
            report_parts.append("📊 Progress Callback: Active")

        # Output information
        report_parts.extend(
            [
                "",
                "📄 Output Information:",
                f"  Size: {status['output_size_display']}",
                f"  Preview: {status['output_preview']!r}",
            ]
        )

        if status.get("awaiting_input_reason"):
            report_parts.extend(
                [
                    "",
                    f"⏸️  Awaiting Input: {status['awaiting_input_reason']}",
                    "Use send_input() to provide the required input.",
                ]
            )

        return "\n".join(report_parts)

    except Exception as e:
        error_info = ErrorHandler.categorize_error(str(e), e)
        logger.error(f"Enhanced status check failed: {error_info.message}")
        return ErrorHandler.format_error_for_ai(error_info)


@mcp.tool()
def get_performance_metrics() -> str:
    """Get detailed performance metrics from logging.

    Provides performance statistics for various operations including
    connection times, command execution times, and optimization data.

    Returns:
        Detailed performance metrics report
    """
    logger.info("Getting performance metrics")

    try:
        metrics = session_manager.get_performance_metrics()

        if not metrics:
            return "📊 No performance metrics available yet."

        report_parts = ["📈 Performance Metrics Report", ""]

        for operation, data in metrics.items():
            report_parts.extend(
                [
                    f"🔧 {operation.title()}:",
                    f"  Executions: {data['count']}",
                    f"  Total Time: {data['total_time']:.3f}s",
                    f"  Average: {data['avg_time']:.3f}s",
                    f"  Min: {data['min_time']:.3f}s",
                    f"  Max: {data['max_time']:.3f}s",
                    "",
                ]
            )

        # Connection profile statistics
        perf_report = session_manager.connection_profiles.get_performance_report()
        if perf_report["total_profiles"] > 0:
            report_parts.extend(
                [
                    "🌐 Connection Profile Statistics:",
                    f"  Total Profiles: {perf_report['total_profiles']}",
                    "",
                ]
            )

            for profile_key, profile_data in perf_report["profiles"].items():
                report_parts.extend(
                    [
                        f"  📍 {profile_key}:",
                        f"    Host: {profile_data['hostname']}",
                        f"    Connections: {profile_data['connect_count']}",
                        f"    Avg Connect Time: {profile_data['avg_connect_time']:.3f}s",
                        f"    Health: {profile_data['connection_health']}",
                    ]
                )

        return "\n".join(report_parts)

    except Exception as e:
        error_info = ErrorHandler.categorize_error(str(e), e)
        logger.error(f"Performance metrics failed: {error_info.message}")
        return ErrorHandler.format_error_for_ai(error_info)


# Export the enhanced server
if __name__ == "__main__":
    mcp.run()
else:
    # When imported, make available for external use
    __all__ = ["mcp", "session_manager"]
