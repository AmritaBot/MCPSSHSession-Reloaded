"""Entry point for mcp-ssh-reloaded.

Supports multiple modes:
    mcp-ssh-reloaded serve mcp        # MCP stdio server (default)
    mcp-ssh-reloaded exec <host> <cmd> # Direct execution (no MCP)
    mcp-ssh-reloaded list             # List active sessions
    mcp-ssh-reloaded close <host>     # Close a session
"""

import argparse
import sys

from .api_types import ConnectionParams
from .services import SSHService


def main(argv: list[str] | None = None) -> None:
    from .logging_manager import get_logger

    _log = get_logger("cli")

    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="mcp-ssh-reloaded",
        description="MCP SSH Session server",
    )
    sub = parser.add_subparsers(dest="mode")

    # serve <sub-mode>
    serve_p = sub.add_parser("serve", help="Start a server")
    serve_sub = serve_p.add_subparsers(dest="serve_mode", required=True)
    serve_sub.add_parser("mcp", help="MCP stdio server (default)")

    # exec <host> <command...>
    exec_p = sub.add_parser("exec", help="Execute a command directly")
    exec_p.add_argument("host")
    exec_p.add_argument("command", nargs="+")
    exec_p.add_argument("-u", "--user")
    exec_p.add_argument("-p", "--port", type=int, default=22)
    exec_p.add_argument("-k", "--key")
    exec_p.add_argument("--sudo-password")
    exec_p.add_argument("-t", "--timeout", type=int, default=30)

    # list
    sub.add_parser("list", help="List active sessions")

    # close <host>
    close_p = sub.add_parser("close", help="Close a session")
    close_p.add_argument("host")
    close_p.add_argument("-u", "--user")
    close_p.add_argument("-p", "--port", type=int, default=22)

    # close-all
    sub.add_parser("close-all", help="Close all sessions")

    args = parser.parse_args(argv)

    if args.mode is None:
        # Default: MCP stdio
        _run_mcp()
    elif args.mode == "serve" and args.serve_mode == "mcp":
        _run_mcp()
    elif args.mode == "exec":
        _run_exec(args)
    elif args.mode == "list":
        _run_list()
    elif args.mode == "close":
        _run_close(args)
    elif args.mode == "close-all":
        _run_close_all()
    else:
        _run_mcp()


def _run_mcp() -> None:
    from .server import mcp

    mcp.run()


def _run_exec(args) -> None:
    svc = SSHService()
    conn = ConnectionParams(
        host=args.host,
        port=args.port,
        username=args.user,
        key_filename=args.key,
        sudo_password=args.sudo_password,
    )
    cmd = " ".join(args.command)
    result = svc.execute(conn, cmd, timeout=args.timeout)
    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    sys.exit(result.exit_code)


def _run_list() -> None:
    svc = SSHService()
    sessions = svc.list_sessions()
    if not sessions:
        print("No active SSH sessions")
        return
    for s in sessions:
        print(f"  {s.session_key}")


def _run_close(args) -> None:
    svc = SSHService()
    svc.close_session(
        ConnectionParams(host=args.host, username=args.user, port=args.port)
    )
    print(f"Closed: {args.user or '(default)'}@{args.host}:{args.port}")


def _run_close_all() -> None:
    svc = SSHService()
    svc.close_all()
    print("All SSH sessions closed")


if __name__ == "__main__":
    main()
