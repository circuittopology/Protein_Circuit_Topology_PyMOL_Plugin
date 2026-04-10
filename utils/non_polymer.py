import logging
from typing import Any

from pymol import cmd
from PyQt5.QtWidgets import QMessageBox

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def show_warning_dialog(self: Any) -> None:
    """
    Shows a warning dialog before removing non-polymer atoms.
    Allows the user to proceed, cancel, or disable the warning for the session.

    Args:
        self: The main GUI class instance.
    """
    if getattr(self, "_suppress_non_polymer_warning", False):
        remove_non_polymer_atoms()
        return

    msg_box = QMessageBox(self)
    msg_box.setWindowTitle("Warning")
    msg_box.setText("All non-polymer elements will be removed.")
    msg_box.setIcon(QMessageBox.Warning)

    continue_btn = msg_box.addButton("Continue", QMessageBox.AcceptRole)
    msg_box.addButton("Cancel", QMessageBox.RejectRole)
    never_show_btn = msg_box.addButton("Don't show again", QMessageBox.DestructiveRole)

    msg_box.exec_()

    clicked = msg_box.clickedButton()

    if clicked == continue_btn:
        remove_non_polymer_atoms()
    elif clicked == never_show_btn:
        self._suppress_non_polymer_warning = True
        remove_non_polymer_atoms()
    else:
        logger.info("User cancelled.")

# generic
def remove_non_polymer_atoms() -> None:
    """
    Removes all non-polymer atoms from the PyMOL session.
    """
    before_atoms = cmd.count_atoms("all")
    cmd.remove("not polymer")
    cmd.refresh()
    after_atoms = cmd.count_atoms("all")
    logger.info("Removed all non-polymer atoms! Atom count has changed from %s to %s", before_atoms, after_atoms)
    cmd.zoom("all")

# generic
def has_non_polymer_atoms() -> bool:
    """
    Checks if there are any non-polymer atoms in the PyMOL session.

    Returns:
        bool: True if non-polymer atoms exist, False otherwise.
    """
    atom_count = cmd.count_atoms("not polymer")
    return atom_count > 0

# generic
def new_file_has_non_polymer_atoms(obj_name: str) -> bool:
    """
    Checks if a specific object contains non-polymer atoms.

    Args:
        obj_name (str): The name of the object to check.

    Returns:
        bool: True if the object contains non-polymer atoms, False otherwise.
    """
    cmd.refresh()
    atom_count = cmd.count_atoms(f"{obj_name} and not polymer")
    return atom_count > 0
