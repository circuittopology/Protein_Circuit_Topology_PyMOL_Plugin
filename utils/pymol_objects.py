"""New improved check for loaded PyMOL objects."""
from __future__ import annotations

import logging

from pymol import cmd
from PyQt5.QtCore import QObject, QTimer, pyqtSignal

logger = logging.getLogger(__name__)

POLL_INTERVAL_MS = 2000


class PymolObjects(QObject):
    """Polls PyMOL's object list and emits `changed` when it differs from the last poll."""

    changed = pyqtSignal(list)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._objects: list[str] = []
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(POLL_INTERVAL_MS)

    @property
    def objects(self) -> list[str]:
        """The object list as of the last poll."""
        return list(self._objects)

    def refresh(self) -> None:
        """Re-read PyMOL's object list and emit `changed` if it moved."""
        try:
            current = cmd.get_object_list()
        except Exception:
            logger.debug("cmd.get_object_list failed during poll", exc_info=True)
            return

        if current != self._objects:
            self._objects = list(current)
            self.changed.emit(self.objects)

    def stop(self) -> None:
        """Stop polling. Called from CTDialog.closeEvent so a hidden dialog leaves no live timer."""
        self._timer.stop()
