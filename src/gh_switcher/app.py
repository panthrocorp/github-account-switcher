from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from gh_switcher import accounts as accounts_mod
from gh_switcher import autostart, config, icons, notifications
from gh_switcher.accounts import GhAccount, load_accounts
from gh_switcher.identity import get_current, set_identity
from gh_switcher.switcher import SwitchError, run_switch
from gh_switcher.tray import get_backend
from gh_switcher.tray.base import MenuItem, TrayBackend


class GhSwitcherApp:
    def __init__(self) -> None:
        self._backend: TrayBackend = get_backend()
        self._accounts: list[GhAccount] = []

    # -- Public ---------------------------------------------------------------

    def run(self) -> None:
        self._backend.run(on_ready=self._on_ready)

    # -- Lifecycle ------------------------------------------------------------

    def _on_ready(self) -> None:
        current_identity = get_current()
        self._accounts = load_accounts()
        config.ensure_exists(self._accounts, current_identity)
        self.refresh()

    def refresh(self) -> None:
        self._accounts = load_accounts()
        active = accounts_mod.active_account(self._accounts)

        icon_path = self._active_icon(active)
        self._backend.set_icon(icon_path)

        tooltip = f"gh: {active.username}" if active else "gh-switcher"
        self._backend.set_tooltip(tooltip)
        self._backend.set_menu(self._build_menu())

    # -- Switch ---------------------------------------------------------------

    def switch_to(self, username: str) -> None:
        try:
            run_switch(username)
        except SwitchError as exc:
            notifications.notify("Switch failed", str(exc))
            return

        identity = config.get_identity(username)
        if identity:
            set_identity(identity.name, identity.email)
        else:
            notifications.notify(
                "No git identity",
                f"No git identity configured for {username!r} — edit accounts.toml",
            )

        self.refresh()

    # -- Menu -----------------------------------------------------------------

    def _build_menu(self) -> list[MenuItem]:
        items: list[MenuItem] = []

        for account in self._accounts:
            username = account.username
            items.append(
                MenuItem(
                    label=username,
                    callback=(lambda u: lambda: self.switch_to(u))(username),
                    checked=account.active,
                )
            )

        items.append(MenuItem(label="", separator=True))
        items.append(MenuItem(label="Refresh", callback=self.refresh))
        items.append(
            MenuItem(
                label="Configure accounts...",
                callback=self._open_config,
            )
        )
        items.append(
            MenuItem(
                label=f"Start on Login {'[✓]' if autostart.is_enabled() else '[ ]'}",
                callback=self._toggle_autostart,
            )
        )
        items.append(MenuItem(label="", separator=True))
        items.append(MenuItem(label="Quit", callback=self._backend.stop))

        return items

    # -- Helpers --------------------------------------------------------------

    def _active_icon(self, active: GhAccount | None) -> Path:
        if active:
            return icons.generate_icon(active.username, active=True)
        # Fallback: grey placeholder
        placeholder = icons.CACHE_DIR / "_placeholder.png"
        if not placeholder.exists():
            icons.CACHE_DIR.mkdir(parents=True, exist_ok=True)
            from PIL import Image

            Image.new("RGBA", (64, 64), (120, 120, 120, 255)).save(placeholder, "PNG")
        return placeholder

    def _open_config(self) -> None:
        path = config.config_path()
        if not path.exists():
            notifications.notify(
                "No config file", "accounts.toml has not been created yet."
            )
            return
        if sys.platform == "linux":
            subprocess.Popen(["xdg-open", str(path)])
        elif sys.platform == "win32":
            subprocess.Popen(["start", "", str(path)], shell=True)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])

    def _toggle_autostart(self) -> None:
        if autostart.is_enabled():
            autostart.disable()
        else:
            autostart.enable()
        self.refresh()
