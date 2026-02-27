from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


HOSTS_FILE = Path.home() / ".config" / "gh" / "hosts.yml"


@dataclass(frozen=True)
class GhAccount:
    username: str
    active: bool


def load_accounts() -> list[GhAccount]:
    """Read accounts from ~/.config/gh/hosts.yml.

    Returns an empty list if gh is not logged in.
    """
    if not HOSTS_FILE.exists():
        return []

    with HOSTS_FILE.open() as fh:
        data = yaml.safe_load(fh) or {}

    github_data = data.get("github.com", {})
    users: dict = github_data.get("users", {})
    active_user: str = github_data.get("user", "")

    return [
        GhAccount(username=username, active=(username == active_user))
        for username in users
    ]


def active_account(accounts: list[GhAccount]) -> GhAccount | None:
    return next((a for a in accounts if a.active), None)
