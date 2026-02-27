from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from PIL import Image

import pystray  # type: ignore[import]

from gh_switcher.tray.base import MenuItem, TrayBackend


class PystrayBackend(TrayBackend):
    def __init__(self) -> None:
        self._icon: pystray.Icon | None = None
        self._image: Image.Image = Image.new("RGBA", (64, 64), (100, 100, 100, 255))
        self._tooltip: str = "gh-switcher"
        self._menu_items: list[MenuItem] = []

    def run(self, on_ready: Callable[[], None]) -> None:
        self._icon = pystray.Icon(
            "gh-switcher",
            self._image,
            self._tooltip,
            menu=self._build_pystray_menu(),
        )
        self._icon.run(setup=lambda icon: on_ready())

    def set_icon(self, image_path: Path) -> None:
        self._image = Image.open(image_path).convert("RGBA")
        if self._icon:
            self._icon.icon = self._image

    def set_tooltip(self, text: str) -> None:
        self._tooltip = text
        if self._icon:
            self._icon.title = text

    def set_menu(self, items: list[MenuItem]) -> None:
        self._menu_items = items
        if self._icon:
            self._icon.menu = self._build_pystray_menu()
            self._icon.update_menu()

    def stop(self) -> None:
        if self._icon:
            self._icon.stop()

    def _build_pystray_menu(self) -> pystray.Menu:
        pystray_items: list[pystray.MenuItem] = []
        for item in self._menu_items:
            if item.separator:
                pystray_items.append(pystray.Menu.SEPARATOR)
                continue
            pystray_items.append(
                pystray.MenuItem(
                    text=item.label,
                    action=item.callback,
                    checked=(lambda i: lambda _: i.checked)(item)
                    if item.checked
                    else None,
                    enabled=item.enabled,
                )
            )
        return pystray.Menu(*pystray_items)
