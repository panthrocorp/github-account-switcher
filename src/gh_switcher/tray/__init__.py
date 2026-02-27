from __future__ import annotations

import sys

from gh_switcher.tray.base import TrayBackend


def get_backend() -> TrayBackend:
    """Return the appropriate TrayBackend for the current platform."""
    if sys.platform == "linux":
        from gh_switcher.tray.xapp import XAppTrayBackend

        return XAppTrayBackend()
    else:
        from gh_switcher.tray.pystray_backend import PystrayBackend

        return PystrayBackend()
