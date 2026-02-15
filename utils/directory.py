import os
from typing import Any

from pymol import cmd
from pymol.Qt import QtWidgets, QtCore

from utils.non_polymer import new_file_has_non_polymer_atoms
from utils.config import WARN_MSG


def choose_file(self: Any) -> None:
    """
    Opens a file dialog to select a structure file (PDB or CIF) for single-file analysis.
    Loads the file into PyMOL and checks for non-polymer atoms.

    Args:
        self: The main GUI class instance.
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
            QtWidgets.QMessageBox.warning(self, "Warning", WARN_MSG)

    else:
        self.selected_file = None

def choose_local_file(self: Any) -> None:
    """
    Opens a file dialog to select a structure file (PDB or CIF) for local analysis.
    Loads the file into PyMOL and checks for non-polymer atoms.

    Args:
        self: The main GUI class instance.
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
            QtWidgets.QMessageBox.warning(self, "Warning", WARN_MSG)

    else:
        self.local_selected_file = None

def choose_local_output_dir(self: Any) -> None:
    """
    Opens a directory dialog to select the output directory for local analysis results.

    Args:
        self: The main GUI class instance.
    """
    dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Directory")
    if dir_path:
        self.selected_output_dir_local = dir_path
        set_label_text_elided(dir_path, self.output_local_label)
    else:
        self.selected_output_dir_local = None

def choose_output_dir(self: Any) -> None:
    """
    Opens a directory dialog to select the output directory for single-file analysis results.

    Args:
        self: The main GUI class instance.
    """
    dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Directory")
    if dir_path:
        self.selected_output_dir = dir_path
        set_label_text_elided(dir_path, self.output_dir_label)
    else:
        self.selected_output_dir = None

def choose_output_dir_multi(self: Any) -> None:
    """
    Opens a directory dialog to select the output directory for multi-file analysis results.

    Args:
        self: The main GUI class instance.
    """
    dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Directory")
    if dir_path:
        self.selected_output_dir_multi = dir_path
        set_label_text_elided(dir_path, self.output_dir_label_multi)
    else:
        self.selected_output_dir_multi = None

def choose_input_dir_multi(self: Any) -> None:
    """
    Opens directory dialog to select the input directory containing PDBs for multi-file analysis.
    Updates the frame selector spinbox based on the number of PDB files found.

    Args:
        self: The main GUI class instance.
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
    Sets the text of a QLabel to an elided version of the file path if it's too long.

    Args:
        file_path (str): The full file path.
        label (QLabel): The label widget to update.
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
