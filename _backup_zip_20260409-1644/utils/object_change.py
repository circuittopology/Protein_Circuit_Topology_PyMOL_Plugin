from pymol.Qt import QtWidgets
from .non_polymer import new_file_has_non_polymer_atoms

#str
def handle_standard_object_change(self: QtWidgets.QWidget, obj_name: str) -> None:
    """
    Handles changes in the selected standard object.
    
    Args:
        self: The QtWidget object.
        obj_name: The object name.
    """
    if obj_name and obj_name != "Select a file.":
        if new_file_has_non_polymer_atoms(obj_name):
            QtWidgets.QMessageBox.warning(self, "Warning",
                                            "The opened file contains non-polymer atoms, which can interfere with Circuit Topology. Please use the 'Remove Non-Polymer Atoms' button to remove them.")
            
#str
def handle_local_object_change(self: QtWidgets.QWidget, obj_name: str) -> None:
    """
    Handles changes in the selected local object.
    
    Args:
        self: The QtWidget object.
        obj_name: The object name.
    """
    self.handle_standard_object_change(obj_name)
    self.get_residue_range(obj_name)
