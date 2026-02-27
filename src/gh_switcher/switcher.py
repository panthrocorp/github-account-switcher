from __future__ import annotations

import subprocess


class SwitchError(Exception):
    """Raised when `gh auth switch` exits non-zero."""


def run_switch(username: str) -> None:
    """Switch the active gh account to *username*.

    Raises:
        SwitchError: if gh exits with a non-zero status.
    """
    result = subprocess.run(
        ["gh", "auth", "switch", "--hostname", "github.com", "--user", username],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise SwitchError(f"gh auth switch failed for {username!r}: {stderr}")
