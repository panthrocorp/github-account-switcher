# github-account-switcher

A lightweight system tray app for switching between multiple GitHub accounts (`gh` CLI) with a single click. Each account can carry its own git identity (name + email), which is applied automatically on switch.

## Features

- System tray icon showing the active account's initials
- One-click account switching via `gh auth switch`
- Per-account git identity (`user.name` / `user.email`) applied on switch
- First-run auto-populates config from current `git config --global`
- Start on login (XDG autostart / winreg / launchd)
- Cross-platform: Linux (Cinnamon/X11 via XApp), Windows and macOS (via pystray)

## Requirements

- Python 3.12+
- [`gh` CLI](https://cli.github.com/) with at least one authenticated account
- **Linux only**: `gir1.2-xapp-1.0` and `python3-gi` system packages

## Installation

```bash
git clone https://github.com/panthrocorp/github-account-switcher.git
cd github-account-switcher

make install        # creates .venv and installs the package
```

> **Linux note**: the venv is created with `--system-site-packages` so the GTK/XApp bindings (system packages) are accessible.

## Usage

```bash
.venv/bin/gh-switcher
# or
.venv/bin/python -m gh_switcher
```

The tray icon appears in your system tray. Right-click (or left-click on Linux) to see the menu:

```
✓  listellm
   panthrocorp
──────────────────
Refresh
Configure accounts...
Start on Login [ ]
──────────────────
Quit
```

## Configuration

On first run, `~/.config/gh-switcher/accounts.toml` is created automatically. The active account is populated from your current `git config --global`; other accounts get stub entries to fill in:

```toml
[listellm]
name = "Your Name"
email = "you@example.com"

[panthrocorp]
name = "Org Bot (set me)"
email = "org@example.com (set me)"
```

Click **Configure accounts...** in the tray menu to open the file in your default editor.

## Development

```bash
make lint       # ruff check
make format     # ruff format
make test       # pytest tests/
```

## Releasing

Releases are driven by [semantic-release](https://semantic-release.gitbook.io/) via GitHub Actions on push to `main`. Commit messages must follow the convention:

| Prefix | Release |
|--------|---------|
| `fix:` | patch |
| `feat:` | minor |
| `breaking:` | major |

## Licence

[MIT](LICENSE)
