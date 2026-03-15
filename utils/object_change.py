import sys
from pathlib import Path
from  typing import Any

from PyQt5.QtWidgets import QMessageBox

from utils.non_polymer import new_file_has_non_polymer_atoms
from utils.config import WARN_MSG

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

def handle_standard_object_change(self: Any, obj_name: str) -> None:
    """
    Handles changes to the selected object in the standard analysis tab.
    Checks for non-polymer atoms and warns the user if found.

    Args:
        self: The main GUI class instance.
        obj_name (str): The name of the newly selected object.
    """
    if obj_name and obj_name != "Select a file.":
        if new_file_has_non_polymer_atoms(obj_name):
            QMessageBox.warning(self, "Warning", WARN_MSG)

#str
def handle_local_object_change(self: Any, obj_name: str) -> None:
    """
    Handles changes to the selected object in the local analysis tab.
    Checks for non-polymer atoms and updates the residue range.

    Args:
        self: The main GUI class instance.
        obj_name (str): The name of the newly selected object.
    """
    self.handle_standard_object_change(obj_name)
    self.get_residue_range(obj_name)
