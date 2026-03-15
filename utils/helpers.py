import sys
from pathlib import Path
from typing import Any

from pymol import cmd
from pymol.Qt import QtCore
from PyQt5.QtWidgets import QPushButton

from utils.config import INFO_BUTTON_STYLE

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

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
    self.timer = QtCore.QTimer(self)
    self.timer.timeout.connect(self.update_list)
    self.timer.timeout.connect(self.update_local_list)
    self.timer.start(1000)

def object_exists(name: str) -> bool:
    """
    Checks if a PyMOL object exists.

    Args:
        name (str): The name of the object.

    Returns:
        bool: True if the object exists, False otherwise.
    """
    return name in cmd.get_names()
