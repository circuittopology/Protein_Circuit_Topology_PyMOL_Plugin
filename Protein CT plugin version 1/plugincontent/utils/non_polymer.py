import os
from pymol import cmd
from pymol.Qt import QtWidgets

def show_warning_dialog(self: QtWidgets.QWidget) -> None:
    """
    Shows a warning dialog before removing non-polymer atoms.
    
    Args:
        self: The QtWidget object.
    """
    # check if user selected don't show again
    if os.environ.get("DISABLE_NON_POLYMER_WARNING") == "1":
        remove_non_polymer_atoms()
        return

    msg_box = QtWidgets.QMessageBox(self)
    msg_box.setWindowTitle("Warning")
    msg_box.setText("All non-polymer elements will be removed.")
    msg_box.setIcon(QtWidgets.QMessageBox.Warning)

    continue_btn = msg_box.addButton("Continue", QtWidgets.QMessageBox.AcceptRole)
    cancel_btn = msg_box.addButton("Cancel", QtWidgets.QMessageBox.RejectRole)
    never_show_btn = msg_box.addButton("Don't show again", QtWidgets.QMessageBox.DestructiveRole)

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
    """Removes non-polymer atoms from all objects in PyMOL."""
    before_atoms = cmd.count_atoms("all")
    cmd.remove("not polymer")
    cmd.refresh()
    after_atoms = cmd.count_atoms("all")
    print(f"Removed all non-polymer atoms!\n Atom count has changed from {before_atoms} to {after_atoms}")
    cmd.zoom("all")

# generic
def has_non_polymer_atoms() -> bool:
    """
    Checks if there are any non-polymer atoms in PyMOL.
    
    Returns:
        True if there are non-polymer atoms, False otherwise.
    """
    atom_count = cmd.count_atoms("not polymer")
    return atom_count > 0

# generic
def new_file_has_non_polymer_atoms(obj_name: str) -> bool:
    """
    Checks if a newly loaded file has non-polymer atoms.
    
    Args:
        obj_name: The object name.
        
    Returns:
        True if the object has non-polymer atoms, False otherwise.
    """
    cmd.refresh()
    atom_count = cmd.count_atoms(f"{obj_name} and not polymer")
    return atom_count > 0