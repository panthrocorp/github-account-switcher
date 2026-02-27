from __future__ import annotations

import subprocess
import sys


def notify(title: str, message: str) -> None:
    """Send a desktop notification. Silent on failure."""
    try:
        if sys.platform == "linux":
            _notify_send(title, message)
        else:
            _plyer_notify(title, message)
    except Exception:
        pass


def _notify_send(title: str, message: str) -> None:
    subprocess.run(
        ["notify-send", "--app-name=gh-switcher", title, message],
        check=False,
        capture_output=True,
    )


def _plyer_notify(title: str, message: str) -> None:
    try:
        from plyer import notification  # type: ignore[import]

        notification.notify(
            title=title,
            message=message,
            app_name="gh-switcher",
            timeout=4,
        )
    except ImportError:
        pass
