from pathlib import Path
from typing import Any

from pymol import cmd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QLabel, QMessageBox

from utils.config import WARN_MSG
from utils.non_polymer import new_file_has_non_polymer_atoms
from utils.validation import (
    legalize_object_name,
    list_structure_files,
    object_exists,
    set_frame_spinbox_bounds,
    validate_structure_file,
)


def _ensure_object_loaded(obj_name: str) -> None:
    if not object_exists(obj_name):
        msg = f"PyMOL did not create the expected object: {obj_name}"
        raise RuntimeError(msg)


def _load_structure_file(self, label, attr_file, attr_obj):
    """Shared helper: open a file dialog, load into PyMOL, check for non-polymer atoms."""
    file_filter = "Structure Files (*.pdb *.cif)"
    file_path, _ = QFileDialog.getOpenFileName(self, "Select Input File", "", file_filter)
    if file_path:
        try:
            input_path = validate_structure_file(file_path)
            obj_name = legalize_object_name(input_path.stem)
            cmd.load(str(input_path), obj_name)
            _ensure_object_loaded(obj_name)
        except Exception as e:  # noqa: BLE001
            setattr(self, attr_file, None)
            setattr(self, attr_obj, None)
            QMessageBox.warning(self, "Error", f"Failed to load structure file:\n{e}")
            return

        set_label_text_elided(str(input_path), label)
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
    selected_dir = QFileDialog.getExistingDirectory(self, "Select Input Directory")
    if not selected_dir:
        self.selected_input_dir_multi = None
        self.available_mol_files = []
        set_frame_spinbox_bounds(self.frame_selector_spinbox, 0)
        return

    dir_path = Path(selected_dir)
    try:
        structure_files = list_structure_files(dir_path)
    except (OSError, ValueError) as e:
        self.selected_input_dir_multi = None
        self.available_mol_files = []
        set_frame_spinbox_bounds(self.frame_selector_spinbox, 0)
        QMessageBox.warning(self, "Error", f"Failed to read input directory:\n{e}")
        return

    self.selected_input_dir_multi = dir_path
    set_label_text_elided(str(dir_path), self.input_dir_label_multi)
    self.available_mol_files = structure_files
    set_frame_spinbox_bounds(self.frame_selector_spinbox, len(structure_files))
    if not structure_files:
        QMessageBox.warning(self, "Error", f"No PDB or CIF files found in the selected directory: {dir_path}.")


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
