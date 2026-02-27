from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("XApp", "1.0")

from gi.repository import GLib, Gtk, XApp  # noqa: E402

from gh_switcher.tray.base import MenuItem, TrayBackend  # noqa: E402


class XAppTrayBackend(TrayBackend):
    def __init__(self) -> None:
        self._icon: XApp.StatusIcon = XApp.StatusIcon()
        self._icon.set_visible(True)
        self._menu: Gtk.Menu = Gtk.Menu()
        self._on_ready: Callable[[], None] | None = None

    # -- TrayBackend interface ------------------------------------------------

    def run(self, on_ready: Callable[[], None]) -> None:
        self._on_ready = on_ready
        GLib.idle_add(self._fire_ready)
        Gtk.main()

    def set_icon(self, image_path: Path) -> None:
        GLib.idle_add(self._icon.set_icon_name, str(image_path))

    def set_tooltip(self, text: str) -> None:
        GLib.idle_add(self._icon.set_tooltip_text, text)

    def set_menu(self, items: list[MenuItem]) -> None:
        GLib.idle_add(self._rebuild_menu, items)

    def stop(self) -> None:
        GLib.idle_add(Gtk.main_quit)

    # -- Internal -------------------------------------------------------------

    def _fire_ready(self) -> bool:
        if self._on_ready:
            self._on_ready()
        return GLib.SOURCE_REMOVE

    def _rebuild_menu(self, items: list[MenuItem]) -> bool:
        # Destroy existing items
        for child in self._menu.get_children():
            self._menu.remove(child)

        for item in items:
            if item.separator:
                self._menu.append(Gtk.SeparatorMenuItem())
                continue

            if item.checked:
                gtk_item = Gtk.CheckMenuItem(label=item.label)
                gtk_item.set_active(True)
                gtk_item.set_draw_as_radio(True)
            else:
                gtk_item = Gtk.MenuItem(label=item.label)

            gtk_item.set_sensitive(item.enabled)

            if item.callback is not None:
                callback = item.callback  # capture for closure

                def _on_activate(
                    _widget: Gtk.MenuItem, cb: Callable = callback
                ) -> None:
                    cb()

                gtk_item.connect("activate", _on_activate)

            self._menu.append(gtk_item)

        self._menu.show_all()
        self._icon.set_secondary_menu(self._menu)
        return GLib.SOURCE_REMOVE
