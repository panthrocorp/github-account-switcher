from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

import platformdirs

from gh_switcher.accounts import GhAccount
from gh_switcher.identity import GitIdentity


CONFIG_DIR = Path(platformdirs.user_config_dir("gh-switcher"))
ACCOUNTS_FILE = CONFIG_DIR / "accounts.toml"


@dataclass(frozen=True)
class AccountConfig:
    username: str
    name: str
    email: str

    def to_identity(self) -> GitIdentity:
        return GitIdentity(name=self.name, email=self.email)


def get_identity(username: str) -> GitIdentity | None:
    """Return the git identity for *username*, or None if not configured."""
    data = _read()
    entry = data.get(username)
    if not entry:
        return None
    name = entry.get("name", "").strip()
    email = entry.get("email", "").strip()
    if not name or not email:
        return None
    return GitIdentity(name=name, email=email)


def ensure_exists(accounts: list[GhAccount], current_identity: GitIdentity) -> None:
    """First-run: create accounts.toml if absent.

    Populates the active account from *current_identity*; other accounts get
    stub entries that the user must fill in.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if ACCOUNTS_FILE.exists():
        return

    data: dict[str, dict[str, str]] = {}
    for account in accounts:
        if account.active:
            data[account.username] = {
                "name": current_identity.name,
                "email": current_identity.email,
            }
        else:
            data[account.username] = {
                "name": f"{account.username} (set me)",
                "email": f"{account.username}@example.com (set me)",
            }

    _write(data)


def config_path() -> Path:
    return ACCOUNTS_FILE


def _read() -> dict[str, dict[str, str]]:
    if not ACCOUNTS_FILE.exists():
        return {}
    with ACCOUNTS_FILE.open("rb") as fh:
        return tomllib.load(fh)


def _write(data: dict[str, dict[str, str]]) -> None:
    lines: list[str] = []
    for section, values in data.items():
        lines.append(f"[{section}]")
        for key, value in values.items():
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'{key} = "{escaped}"')
        lines.append("")
    ACCOUNTS_FILE.write_text("\n".join(lines), encoding="utf-8")
