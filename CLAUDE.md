# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Setup
make install              # create .venv (--system-site-packages) and install editable

# Quality
make lint                 # ruff check src/
make format               # ruff format src/
make test                 # pytest tests/

# Run
.venv/bin/gh-switcher
.venv/bin/python -m gh_switcher
```

> **Linux venv note**: must use `--system-site-packages` so the venv can access `gi` (PyGObject), which is a system package not available on PyPI.

## Build System

Hatchling via `pyproject.toml`. Source layout: `src/gh_switcher/`. Entry point: `gh-switcher = "gh_switcher.__main__:main"`. Requires Python >= 3.12.

## Architecture

### Data Flow

1. **Startup**: `__main__` creates `GhSwitcherApp` which selects the platform tray backend, reads `gh` CLI state, ensures the user config exists, and builds the tray menu.
2. **Account switch**: User selects an account from the tray menu. `switcher.run_switch()` shells out to `gh auth switch`. On success, `config.get_identity()` looks up the git identity from `accounts.toml` and `identity.set_identity()` writes `git config --global user.name/email`.
3. **Refresh**: After every switch (or manual refresh), the account list is re-read from `~/.config/gh/hosts.yml`, the icon and menu are rebuilt.

### Module Responsibilities

| Module | Purpose |
|--------|---------|
| `app.py` | `GhSwitcherApp` orchestrator: startup lifecycle, menu construction, switch dispatch |
| `accounts.py` | Reads `~/.config/gh/hosts.yml` (gh CLI state) to enumerate accounts and active user |
| `config.py` | Manages `~/.config/gh-switcher/accounts.toml` via `platformdirs`. TOML sections keyed by username with `name` and `email` fields. Auto-created on first run |
| `identity.py` | Reads/writes `git config --global user.name` and `user.email` |
| `switcher.py` | Runs `gh auth switch --hostname github.com --user <username>`. Raises `SwitchError` on failure |
| `icons.py` | Generates 64x64 PNG avatar icons from username initials with MD5-hashed colour. Active accounts get a green border. Cached at `platformdirs.user_cache_dir("gh-switcher")/icons/` |
| `autostart.py` | Cross-platform login-item management: `.desktop` file (Linux), registry key (Windows), LaunchAgent plist (macOS) |
| `notifications.py` | Desktop notifications: `notify-send` on Linux, `plyer` elsewhere (optional) |
| `tray/base.py` | `TrayBackend` ABC and `MenuItem` dataclass |
| `tray/xapp.py` | Linux backend: GTK3 + `XApp.StatusIcon` |
| `tray/pystray_backend.py` | macOS/Windows backend: `pystray` library |

### Key Files Outside the Package

- `~/.config/gh/hosts.yml` -- read-only, owned by `gh` CLI. Source of truth for logged-in accounts.
- `~/.config/gh-switcher/accounts.toml` -- user-editable git identity mapping per account.

## Platform Dependencies

**All platforms**: `gh` CLI must be installed and have at least one authenticated account.

**Linux**: Requires system packages `python3-xapp` and `python3-gi` (GTK3 introspection) for the tray icon. `notify-send` is optional for notifications. DejaVu fonts are optional for icon rendering.

**macOS / Windows**: The `pystray` pip dependency is installed automatically (conditional in `pyproject.toml`).

## Code Conventions

- `from __future__ import annotations` is used throughout.
- Frozen dataclasses for data structures (`GhAccount`, `AccountConfig`, `MenuItem`, `GitIdentity`).
- No async code; all subprocess calls are synchronous.
- Custom exceptions are defined close to their raising site (`SwitchError` in `switcher.py`).
- Platform branching uses `sys.platform` string checks.
