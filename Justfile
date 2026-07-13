# Justfile for mcp-ssh-reloaded project

# Install project dependencies
install:
    @echo "Installing dependencies..."
    uv sync

# Run all tests, including integration tests.
# Set environment variables before calling this recipe:
#   SSH_TEST_HOST=myhost just test
#   SSH_TEST_HOST=myhost SSH_TEST_USER=admin SSH_TEST_PASSWORD=secret just test
#   SSH_TEST_HOST=myhost SSH_TEST_USER=admin SSH_TEST_SUDO_PASSWORD=secret just test
#   SSH_TEST_HOST=router SSH_TEST_USER=admin SSH_TEST_PASSWORD=cisco SSH_TEST_ENABLE_PASSWORD=enable just test
#
# Or use the convenience aliases below (test-basic, test-sudo, test-network)
test:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Running tests..."
    echo ""

    # Show what environment variables are set
    echo "SSH test environment variables:"
    echo "  SSH_TEST_HOST='${SSH_TEST_HOST:-<not set>}'"
    echo "  SSH_TEST_USER='${SSH_TEST_USER:-<not set>}'"
    if [ -n "${SSH_TEST_PASSWORD:-}" ]; then echo "  SSH_TEST_PASSWORD='***'"; else echo "  SSH_TEST_PASSWORD='<not set>'"; fi
    echo "  SSH_TEST_KEY_FILE='${SSH_TEST_KEY_FILE:-<not set>}'"
    echo "  SSH_TEST_PORT='${SSH_TEST_PORT:-22}'"
    if [ -n "${SSH_TEST_SUDO_PASSWORD:-}" ]; then echo "  SSH_TEST_SUDO_PASSWORD='***'"; else echo "  SSH_TEST_SUDO_PASSWORD='<not set>'"; fi
    if [ -n "${SSH_TEST_ENABLE_PASSWORD:-}" ]; then echo "  SSH_TEST_ENABLE_PASSWORD='***'"; else echo "  SSH_TEST_ENABLE_PASSWORD='<not set>'"; fi
    echo ""

    # Run pytest
    if [ -n "${SSH_TEST_HOST:-}" ]; then
        echo "Running integration tests against ${SSH_TEST_HOST}..."
    else
        echo "Running unit tests only (set SSH_TEST_HOST to run integration tests)"
    fi
    echo ""

    uv run pytest tests/ -v -s

# Convenience recipe: Run basic integration tests (excludes network/mikrotik tests)
# Usage: just test-basic host=myhost [user=myuser] [password=pass] [keyfile=~/.ssh/id_rsa] [port=22]
test-basic host user="" password="" keyfile="" port="22":
    #!/usr/bin/env bash
    set -euo pipefail
    export SSH_TEST_HOST="{{host}}"
    [ -n "{{user}}" ] && export SSH_TEST_USER="{{user}}"
    [ -n "{{password}}" ] && export SSH_TEST_PASSWORD="{{password}}"
    [ -n "{{keyfile}}" ] && export SSH_TEST_KEY_FILE="{{keyfile}}"
    [ "{{port}}" != "22" ] && export SSH_TEST_PORT="{{port}}"
    uv run pytest tests/ -v -s --ignore=tests/test_mikrotik.py --ignore=tests/test_network_devices.py

# Convenience recipe: Run tests with sudo password
# Usage: just test-sudo host=myhost sudo_password=pass [user=myuser] [password=pass] [keyfile=~/.ssh/id_rsa]
test-sudo host sudo_password user="" password="" keyfile="":
    #!/usr/bin/env bash
    set -euo pipefail
    export SSH_TEST_HOST="{{host}}"
    [ -n "{{user}}" ] && export SSH_TEST_USER="{{user}}"
    export SSH_TEST_SUDO_PASSWORD="{{sudo_password}}"
    [ -n "{{password}}" ] && export SSH_TEST_PASSWORD="{{password}}"
    [ -n "{{keyfile}}" ] && export SSH_TEST_KEY_FILE="{{keyfile}}"
    uv run pytest tests/ -v -s --ignore=tests/test_mikrotik.py --ignore=tests/test_network_devices.py

# Convenience recipe: Run network device tests (with enable password)
# Usage: just test-network host=router password=cisco enable_password=enable [user=admin]
test-network host password enable_password user="":
    #!/usr/bin/env bash
    set -euo pipefail
    export SSH_TEST_HOST="{{host}}"
    [ -n "{{user}}" ] && export SSH_TEST_USER="{{user}}"
    export SSH_TEST_PASSWORD="{{password}}"
    export SSH_TEST_ENABLE_PASSWORD="{{enable_password}}"
    uv run pytest tests/test_network_devices.py -v -s

# Convenience recipe: Run concurrency tests
# Usage: just test-concurrency host=myhost sudo_password=pass [user=myuser] [password=pass] [keyfile=~/.ssh/id_rsa]
test-concurrency host sudo_password user="" password="" keyfile="":
    #!/usr/bin/env bash
    set -euo pipefail
    export SSH_TEST_HOST="{{host}}"
    [ -n "{{user}}" ] && export SSH_TEST_USER="{{user}}"
    export SSH_TEST_SUDO_PASSWORD="{{sudo_password}}"
    [ -n "{{password}}" ] && export SSH_TEST_PASSWORD="{{password}}"
    [ -n "{{keyfile}}" ] && export SSH_TEST_KEY_FILE="{{keyfile}}"
    uv run pytest tests/test_concurrency.py -v -s

# Run the MCP SSH Session server (MCP stdio)
# Usage:
#   just run
#   just run default-timeout=60 max-workers=20
#   MCP_SSH_DEFAULT_TIMEOUT=60 just run
run default-timeout="" max-workers="" connect-timeout="" max-file-bytes="" max-output-bytes="" interactive-mode="" async-default-timeout="" background-monitor-max-timeout="" normal-idle-timeout="" package-manager-idle-timeout="" terminal-width="" terminal-height="" log-dir="" mikrotik-auto-paging="" pty-aware-validation="":
    @echo "Starting MCP SSH Session server..."
    uv run mcp-ssh serve mcp \
      {{ if default-timeout != "" { "--default-timeout " + default-timeout } else { "" } }} \
      {{ if max-workers != "" { "--max-workers " + max-workers } else { "" } }} \
      {{ if connect-timeout != "" { "--connect-timeout " + connect-timeout } else { "" } }}

# Run linting + type checks
lint:
    @echo "Running ruff..."
    uv run ruff check .
    @echo "Running pyright..."
    uv run pyright .

# Format code
fmt:
    uv run ruff format .

# Fix auto-fixable lint issues
fix:
    uv run ruff check --fix .

# Build Docker image
docker-build:
    docker build -t mcp-ssh-reloaded .

# Run Docker container (MCP stdio)
docker-run:
    docker run --rm -i \
        -v ~/.ssh:/mounts/ssh-keys:ro \
        mcp-ssh-reloaded

# Clean up build artifacts, cache, and log files
clean:
    @echo "Cleaning up build artifacts, cache, and log files..."
    rm -rf dist/ build/ __pycache__/ .pytest_cache/ .venv/
    find . -name "*.pyc" -exec rm -f {} +
    find . -name "*.log" -exec rm -f {} +
    @echo "Cleanup complete."
# Convenience recipe: Run Mikrotik tests
# Usage: just test-mikrotik host=router [user=] [password=cisco] [enable_password=enable] [port=22]
test-mikrotik host user="" password="" enable_password="" port="22":
    #!/usr/bin/env bash
    set -euo pipefail
    export SSH_TEST_HOST="{{host}}"
    [ -n "{{user}}" ] && export SSH_TEST_USER="{{user}}"
    [ -n "{{password}}" ] && export SSH_TEST_PASSWORD="{{password}}"
    [ -n "{{enable_password}}" ] && export SSH_TEST_ENABLE_PASSWORD="{{enable_password}}"
    [ "{{port}}" != "22" ] && export SSH_TEST_PORT="{{port}}"
    uv run pytest tests/test_mikrotik.py -v -s
