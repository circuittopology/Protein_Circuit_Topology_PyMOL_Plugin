import os
from typing import Any

from pymol import cmd
from PyQt5.QtWidgets import QMessageBox

def show_warning_dialog(self: Any) -> None:
    """
    Shows a warning dialog before removing non-polymer atoms.
    Allows the user to proceed, cancel, or disable the warning for the session.

    Args:
        self: The main GUI class instance.
    """
    # check if user selected don't show again
    if os.environ.get("DISABLE_NON_POLYMER_WARNING") == "1":
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
        os.environ["DISABLE_NON_POLYMER_WARNING"] = "1"
        print("User chose to never show this warning again.")
        remove_non_polymer_atoms()
    else:
        print("User cancelled.")

# generic
def remove_non_polymer_atoms() -> None:
    """
    Removes all non-polymer atoms from the PyMOL session.
    """
    before_atoms = cmd.count_atoms("all")
    cmd.remove("not polymer")
    cmd.refresh()
    after_atoms = cmd.count_atoms("all")
    print(f"""Removed all non-polymer atoms!
          Atom count has changed from {before_atoms} to {after_atoms}""")
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
