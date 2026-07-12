# Interactive Mode

Enabled by default (v0.2.0+). Attaches a `pyte` VT100 terminal emulator to each
SSH shell for screen-aware interaction.

## Features

- **Terminal emulator** per session — screen buffer, cursor position, dimensions
- **Mode inference** — detects `shell`, `editor`, `pager`, `password_prompt`
- **Screen snapshot** via `read_screen` MCP tool
- **Key sending** via `send_keys` MCP tool
- **Mode-aware awaiting-input** — editors aren't falsely flagged
- **Auto pager handling** — pagers auto-quit with `q`

## Disable

```bash
export MCP_SSH_INTERACTIVE_MODE=0
```

Or in MCP config:

```json
{ "env": { "MCP_SSH_INTERACTIVE_MODE": "0" } }
```

## MCP Tools

### `read_screen`

Returns screen lines, cursor (x, y), width, height.

```json
{ "host": "myserver", "max_lines": 24 }
```

### `send_keys`

Send special keys to the interactive session.

```json
{ "host": "myserver", "keys": "<esc>:wq<enter>" }
```

Supported tokens: `<enter>`, `<esc>`, `<tab>`, `<ctrl-c>`, `<ctrl-d>`,
`<ctrl-z>`, `<up>`, `<down>`, `<left>`, `<right>`, `<space>`.

## Mode Inference

Detected from screen content automatically:

| Mode | Trigger |
|------|---------|
| `editor` | `-- INSERT --`, `-- VISUAL --`, many `~` lines, "GNU nano" |
| `pager` | `(END)` at end, `--More--`, lone `:` |
| `password_prompt` | `password:` or `passphrase:` at end of last line |
| `shell` | Prompt pattern matches last line |
