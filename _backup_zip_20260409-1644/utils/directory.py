import os

from pymol import cmd
from pymol.Qt import QtWidgets, QtCore

from .non_polymer import new_file_has_non_polymer_atoms

def choose_file(self: QtWidgets.QWidget) -> None:
    """
    Opens a file dialog to select an input structure file.
    
    Args:
        self: The QtWidget object (CTDialog instance) calling this function.
    """
    file_filter = "Structure Files (*.pdb *.cif)"
    file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Input File", "", file_filter)

    if file_path:
        self.selected_file = file_path
        set_label_text_elided(file_path, self.dir_label)
        obj_name = os.path.splitext(os.path.basename(file_path))[0]
        cmd.load(file_path, obj_name)
        obj_name = obj_name.replace(" ", "_")
        self.selected_obj_name = obj_name

        # check for non-polymer atoms
        if new_file_has_non_polymer_atoms(obj_name):
            QtWidgets.QMessageBox.warning(self, "Warning",
                                            "The opened file contains non-polymer atoms, which can interfere with Circuit Topology.  Please use the 'Remove Non-Polymer Atoms' button to remove them.")

    else:
        self.selected_file = None

def choose_local_file(self: QtWidgets.QWidget) -> None:
    """
    Opens a file dialog to select a local input structure file.
    
    Args:
        self: The QtWidget object (CTDialog instance) calling this function.
    """
    file_filter = "Structure Files (*.pdb *.cif)"
    file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Input File", "", file_filter)

    if file_path:
        self.local_selected_file = file_path
        set_label_text_elided(file_path, self.local_dir_label)
        obj_name = os.path.splitext(os.path.basename(file_path))[0]
        cmd.load(file_path, obj_name)
        obj_name = obj_name.replace(" ", "_")
        self.local_selected_obj_name = obj_name
        # check for non-polymer atoms
        if new_file_has_non_polymer_atoms(obj_name):
            QtWidgets.QMessageBox.warning(self, "Warning",
                                            "The opened file contains non-polymer atoms, which can interfere with Circuit Topology. Please use the 'Remove Non-Polymer Atoms' button to remove them.")

    else:
        self.local_selected_file = None

def choose_local_output_dir(self: QtWidgets.QWidget) -> None:
    """
    Opens a dialog to choose a local output directory.
    
    Args:
        self: The QtWidget object (CTDialog instance) calling this function.
    """
    dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Directory")
    if dir_path:
        self.selected_output_dir_local = dir_path
        set_label_text_elided(dir_path, self.output_local_label)
    else:
        self.selected_output_dir_local = None

def choose_output_dir(self: QtWidgets.QWidget) -> None:
    """
    Opens a dialog to choose an output directory.
    
    Args:
        self: The QtWidget object (CTDialog instance) calling this function.
    """
    dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Directory")
    if dir_path:
        self.selected_output_dir = dir_path
        set_label_text_elided(dir_path, self.output_dir_label)
    else:
        self.selected_output_dir = None

def choose_output_dir_multi(self: QtWidgets.QWidget) -> None:
    """
    Opens a dialog to choose a multi-file output directory.
    
    Args:
        self: The QtWidget object (CTDialog instance) calling this function.
    """
    dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Directory")
    if dir_path:
        self.selected_output_dir_multi = dir_path
        set_label_text_elided(dir_path, self.output_dir_label_multi)
    else:
        self.selected_output_dir_multi = None

# Added: Gets the pdb files and their range for single frame analysis after getting the output directory
def choose_input_dir_multi(self: QtWidgets.QWidget) -> None:
    """
    Opens a dialog to choose a multi-file input directory.
    
    Args:
        self: The QtWidget object (CTDialog instance) calling this function.
    """
    dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Input Directory")
    if dir_path:
        self.selected_input_dir_multi = dir_path
        set_label_text_elided(dir_path, self.input_dir_label_multi)
        pdb_files = sorted([f.replace(" ", "_") for f in os.listdir(dir_path) if f.endswith(".pdb")])
        self.available_mol_files = pdb_files
        self.frame_selector_spinbox.setMaximum(len(pdb_files))
    else:
        self.selected_input_dir_multi = None


def set_label_text_elided(file_path: str, label: QtWidgets.QLabel) -> None:
    """
    Sets elided text on a QLabel.
    
    Args:
        file_path: The text to set.
        label: The QLabel to update.
    """
    font_metrics = label.fontMetrics()

    available_width = label.width() - 10

    elided_text = font_metrics.elidedText(
        file_path, 
        QtCore.Qt.ElideMiddle,
        available_width
    )
    
    label.setText(elided_text)
    label.setToolTip(file_path)