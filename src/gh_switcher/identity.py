from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class GitIdentity:
    name: str
    email: str


def get_current() -> GitIdentity:
    """Read git config --global user.name and user.email."""
    name = _git_config("user.name")
    email = _git_config("user.email")
    return GitIdentity(name=name, email=email)


def set_identity(name: str, email: str) -> None:
    """Write git config --global user.name and user.email."""
    subprocess.run(
        ["git", "config", "--global", "user.name", name],
        check=True,
    )
    subprocess.run(
        ["git", "config", "--global", "user.email", email],
        check=True,
    )


def _git_config(key: str) -> str:
    result = subprocess.run(
        ["git", "config", "--global", key],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()
