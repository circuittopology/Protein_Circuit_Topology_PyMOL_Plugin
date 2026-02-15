import sys
from pathlib import Path
from pymol.Qt import QtWidgets
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
# pylint: disable=wrong-import-position
from utils.non_polymer import new_file_has_non_polymer_atoms

#str
def handle_standard_object_change(self, obj_name):
    if obj_name and obj_name != "Select a file.":
        if new_file_has_non_polymer_atoms(obj_name):
            QtWidgets.QMessageBox.warning(self, "Warning",
                                            "The opened file contains non-polymer atoms, which can interfere with Circuit Topology. Please use the 'Remove Non-Polymer Atoms' button to remove them.")
            
#str
def handle_local_object_change(self, obj_name):
    self.handle_standard_object_change(obj_name)
    self.get_residue_range(obj_name)
