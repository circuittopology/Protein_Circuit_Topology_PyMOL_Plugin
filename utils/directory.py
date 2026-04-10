import os
from typing import Any

from pymol import cmd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QLabel

from utils.non_polymer import new_file_has_non_polymer_atoms
from utils.config import WARN_MSG


def _load_structure_file(self, label, attr_file, attr_obj):
    """Shared helper: open a file dialog, load into PyMOL, check for non-polymer atoms."""
    file_filter = "Structure Files (*.pdb *.cif)"
    file_path, _ = QFileDialog.getOpenFileName(self, "Select Input File", "", file_filter)
    if file_path:
        set_label_text_elided(file_path, label)
        obj_name = os.path.splitext(os.path.basename(file_path))[0]
        cmd.load(file_path, obj_name)
        obj_name = obj_name.replace(" ", "_")
        setattr(self, attr_file, file_path)
        setattr(self, attr_obj, obj_name)
        if new_file_has_non_polymer_atoms(obj_name):
            QMessageBox.warning(self, "Warning", WARN_MSG)
    else:
        setattr(self, attr_file, None)


def _choose_output_dir(self, attr_name, label):
    """Shared helper: open a directory dialog and store the result."""
    dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
    if dir_path:
        setattr(self, attr_name, dir_path)
        set_label_text_elided(dir_path, label)
    else:
        setattr(self, attr_name, None)


def choose_file(self: Any) -> None:
    _load_structure_file(self, self.dir_label, "selected_file", "selected_obj_name")

def choose_local_file(self: Any) -> None:
    _load_structure_file(self, self.local_dir_label, "local_selected_file", "local_selected_obj_name")

def choose_local_output_dir(self: Any) -> None:
    _choose_output_dir(self, "selected_output_dir_local", self.output_local_label)

def choose_output_dir(self: Any) -> None:
    _choose_output_dir(self, "selected_output_dir", self.output_dir_label)

def choose_output_dir_multi(self: Any) -> None:
    _choose_output_dir(self, "selected_output_dir_multi", self.output_dir_label_multi)

def choose_input_dir_multi(self: Any) -> None:
    """
    Opens directory dialog to select the input directory containing PDBs for multi-file analysis.
    Updates the frame selector spinbox based on the number of PDB files found.

    Args:
        self: The main GUI class instance.
    """
    dir_path = QFileDialog.getExistingDirectory(self, "Select Input Directory")
    if dir_path:
        self.selected_input_dir_multi = dir_path
        set_label_text_elided(dir_path, self.input_dir_label_multi)
        pdb_files = sorted([f.replace(" ", "_") for f in os.listdir(dir_path) if f.endswith(".pdb")])
        self.available_mol_files = pdb_files
        self.frame_selector_spinbox.setMaximum(len(pdb_files))
    else:
        self.selected_input_dir_multi = None


def set_label_text_elided(file_path: str, label: QLabel) -> None:
    """
    Sets the text of a QLabel to an elided version of the file path if it's too long.

    Args:
        file_path (str): The full file path.
        label (QLabel): The label widget to update.
    """
    font_metrics = label.fontMetrics()

    available_width = label.width() - 10

    elided_text = font_metrics.elidedText(file_path, Qt.ElideMiddle, available_width)
    label.setText(elided_text)
    label.setToolTip(file_path)