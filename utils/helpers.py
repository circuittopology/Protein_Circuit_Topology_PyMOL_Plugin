import os
import tempfile
from contextlib import contextmanager
from typing import Any

from pymol import cmd
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QLabel

from utils.config import INFO_BUTTON_STYLE


def update_chain_combo_box(self: Any) -> None:
    """
    Updates the chain combo box with the chains available in the currently selected object.

    Args:
        self: The main GUI class instance.
    """
    self.chain_combo_box.clear()
    self.chain_combo_box.addItems(self.curr_chain_residues.keys())

def make_info_button(tooltip: str) -> QPushButton:
    """
    Creates a small info button with a tooltip.

    Args:
        tooltip (str): The text to display in the tooltip.

    Returns:
        QPushButton: The configured info button.
    """
    btn = QPushButton("ⓘ")
    btn.setFixedWidth(20)
    btn.setFlat(True)
    btn.setStyleSheet(INFO_BUTTON_STYLE)
    btn.setToolTip(tooltip)
    return btn

def init_timers(self: Any) -> None:
    """
    Initializes timers for updating object lists.

    Args:
        self: The main GUI class instance.
    """
    self.timer = QTimer(self)
    self.timer.timeout.connect(self._poll_pymol_objects)
    self.timer.start(2000)

def _poll_pymol_objects(self: Any) -> None:
    """Single poll that refreshes both object dropdowns from one cmd call."""
    from utils.updates import update_list, update_local_list
    new_objects = cmd.get_object_list()
    update_list(self, new_objects)
    update_local_list(self, new_objects)

def object_exists(name: str) -> bool:
    """
    Checks if a PyMOL object exists.

    Args:
        name (str): The name of the object.

    Returns:
        bool: True if the object exists, False otherwise.
    """
    return name in cmd.get_names()


@contextmanager
def temp_pdb_export(selection, state=None):
    """Save a PyMOL selection to a temporary PDB file, yield the path, then clean up."""
    tmp = tempfile.NamedTemporaryFile(suffix=".pdb", delete=False)
    tmp_path = tmp.name
    tmp.close()
    cmd.save(tmp_path, selection, state=state or cmd.get_state())
    try:
        yield tmp_path
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def make_param_row(label_text, tooltip, spinbox):
    """Create a standard parameter row layout with label, info button, and spinbox."""
    row = QHBoxLayout()
    row.addWidget(QLabel(label_text))
    row.addWidget(make_info_button(tooltip))
    row.addStretch()
    row.addWidget(spinbox)
    return row