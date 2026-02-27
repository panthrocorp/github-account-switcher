from __future__ import annotations

import sys
from pathlib import Path

_DESKTOP_DIR = Path.home() / ".config" / "autostart"
_DESKTOP_FILE = _DESKTOP_DIR / "gh-switcher.desktop"
_DESKTOP_CONTENT = """\
[Desktop Entry]
Type=Application
Name=GitHub Account Switcher
Exec={exec}
X-GNOME-Autostart-enabled=true
Hidden=false
NoDisplay=false
Comment=System tray switcher for gh CLI accounts
"""


def is_enabled() -> bool:
    if sys.platform == "linux":
        return _DESKTOP_FILE.exists()
    if sys.platform == "win32":
        return _winreg_get() is not None
    if sys.platform == "darwin":
        return _plist_path().exists()
    return False


def enable() -> None:
    if sys.platform == "linux":
        _desktop_enable()
    elif sys.platform == "win32":
        _winreg_enable()
    elif sys.platform == "darwin":
        _launchd_enable()


def disable() -> None:
    if sys.platform == "linux":
        _DESKTOP_FILE.unlink(missing_ok=True)
    elif sys.platform == "win32":
        _winreg_disable()
    elif sys.platform == "darwin":
        _plist_path().unlink(missing_ok=True)


# -- Linux -------------------------------------------------------------------


def _desktop_enable() -> None:
    _DESKTOP_DIR.mkdir(parents=True, exist_ok=True)
    exec_path = sys.executable
    # Prefer the installed script if available on PATH
    import shutil

    script = shutil.which("gh-switcher")
    if script:
        exec_path = script
    _DESKTOP_FILE.write_text(_DESKTOP_CONTENT.format(exec=exec_path), encoding="utf-8")


# -- Windows ------------------------------------------------------------------

_REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_REG_VALUE = "GhSwitcher"


def _winreg_get() -> str | None:
    try:
        import winreg  # type: ignore[import]

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_KEY) as key:
            value, _ = winreg.QueryValueEx(key, _REG_VALUE)
            return value
    except Exception:
        return None


def _winreg_enable() -> None:
    import winreg  # type: ignore[import]
    import shutil

    exec_path = shutil.which("gh-switcher") or sys.executable
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, _REG_KEY, 0, winreg.KEY_SET_VALUE
    ) as key:
        winreg.SetValueEx(key, _REG_VALUE, 0, winreg.REG_SZ, exec_path)


def _winreg_disable() -> None:
    import winreg  # type: ignore[import]

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _REG_KEY, 0, winreg.KEY_SET_VALUE
        ) as key:
            winreg.DeleteValue(key, _REG_VALUE)
    except FileNotFoundError:
        pass


# -- macOS --------------------------------------------------------------------

_PLIST_LABEL = "com.gh-switcher"
_PLIST_TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{label}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{exec}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""


def _plist_path() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / f"{_PLIST_LABEL}.plist"


def _launchd_enable() -> None:
    import shutil

    exec_path = shutil.which("gh-switcher") or sys.executable
    plist = _plist_path()
    plist.parent.mkdir(parents=True, exist_ok=True)
    plist.write_text(
        _PLIST_TEMPLATE.format(label=_PLIST_LABEL, exec=exec_path),
        encoding="utf-8",
    )
