from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MenuItem:
    label: str
    callback: Callable[[], None] | None = None
    checked: bool = False
    separator: bool = False
    enabled: bool = True


class TrayBackend(ABC):
    """Platform-agnostic tray icon abstraction."""

    @abstractmethod
    def run(self, on_ready: Callable[[], None]) -> None:
        """Start the tray event loop. Blocks until stop() is called."""

    @abstractmethod
    def set_icon(self, image_path: Path) -> None:
        """Update the tray icon to the image at *image_path*."""

    @abstractmethod
    def set_tooltip(self, text: str) -> None:
        """Set the tooltip / hover text."""

    @abstractmethod
    def set_menu(self, items: list[MenuItem]) -> None:
        """Rebuild the context menu from *items*."""

    @abstractmethod
    def stop(self) -> None:
        """Quit the tray and event loop."""
