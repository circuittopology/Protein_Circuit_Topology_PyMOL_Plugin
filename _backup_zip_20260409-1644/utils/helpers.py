from pymol import cmd
from pymol.Qt import QtWidgets, QtCore

from .config import INFO_BUTTON_STYLE

def update_chain_combo_box(self: QtWidgets.QWidget) -> None:
    """
    Updates the chain combo box with current chain residues.
    
    Args:
        self: The QtWidget object.
    """
    self.chain_combo_box.clear()
    self.chain_combo_box.addItems(self.curr_chain_residues.keys())

def make_info_button(tooltip: str) -> QtWidgets.QPushButton:
    """
    Creates an info button with a tooltip.
    
    Args:
        tooltip: The tooltip text.
        
    Returns:
        A styled QPushButton.
    """
    btn = QtWidgets.QPushButton("ⓘ")
    btn.setFixedWidth(20)
    btn.setFlat(True)
    btn.setStyleSheet(INFO_BUTTON_STYLE)
    btn.setToolTip(tooltip)
    return btn

def init_timers(self: QtWidgets.QWidget) -> None:
    """
    Initializes timers for updating lists.
    
    Args:
        self: The QtWidget object.
    """
    self.timer = QtCore.QTimer(self)
    self.timer.timeout.connect(self.update_list)
    self.timer.timeout.connect(self.update_local_list)
    self.timer.start(1000)
    
def object_exists(name: str) -> bool:
    """
    Checks if a given object name exists in PyMOL.
    
    Args:
        name: The object name.
        
    Returns:
        True if the object exists, False otherwise.
    """
    return name in cmd.get_names()
