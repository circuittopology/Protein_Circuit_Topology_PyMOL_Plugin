"""
Utility functions for handling trajectory files in the PyMOL plugin.
"""
import logging
from typing import Any

from pymol import cmd
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from utils.helpers import resolve_output_path
from utils.non_polymer import remove_non_polymer_atoms
from utils.validation import (
    legalize_object_name,
    list_structure_files,
    object_exists,
    object_selection,
    selection_has_atoms,
    set_frame_spinbox_bounds,
    validate_structure_file,
    validate_trajectory_file,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def select_mol_file(self: Any) -> None:
    """
    Opens a file dialog to select a structure file (PDB or CIF) for trajectory analysis.
    Loads the file into PyMOL.

    Args:
        self: The main GUI class instance.
    """
    fname, _ = QFileDialog.getOpenFileName(self, "Select PDB file", "", "Structure files (*.pdb *.cif)")
    if fname:
        try:
            mol_path = validate_structure_file(fname)
            mol_name = legalize_object_name(mol_path.stem)
            cmd.load(str(mol_path), mol_name)
            if not object_exists(mol_name):
                msg = f"PyMOL did not create the expected object: {mol_name}"
                raise RuntimeError(msg)  # noqa: TRY301
        except Exception as e:  # noqa: BLE001
            QMessageBox.warning(self, "Error", f"Failed to load molecule file:\n{e}")
            return

        self.traj_mol_path = str(mol_path)
        self.traj_mol_label.setText(str(mol_path))
        self.protein_name = mol_name

# Gets the trajectory file
def select_xtc_file(self: Any) -> None:
    """
    Opens a file dialog to select a trajectory file (XTC, DCD, TRR, NC).
    Loads the trajectory into PyMOL and removes non-polymer atoms.

    Args:
        self: The main GUI class instance.
    """
    fname, _ = QFileDialog.getOpenFileName(self, "Select trajectory file", "", "Trajectory files (*.xtc *.dcd *.trr *.nc)")
    if fname:
        protein_name = getattr(self, "protein_name", None)
        if not isinstance(protein_name, str) or not object_exists(protein_name):
            QMessageBox.warning(self, "Error", "Please load a matching PDB/CIF molecule before loading a trajectory.")
            return
        try:
            traj_path = validate_trajectory_file(fname)
            cmd.load_traj(str(traj_path), object=protein_name, state=1)
            if cmd.count_states(object_selection(protein_name)) < 1:
                msg = "The trajectory did not add any states to the loaded molecule."
                raise RuntimeError(msg)  # noqa: TRY301
            remove_non_polymer_atoms()
        except Exception as e:  # noqa: BLE001
            QMessageBox.warning(self, "Error", f"Failed to load trajectory file:\n{e}")
            return

        self.traj_xtc_path = str(traj_path)
        self.traj_xtc_label.setText(str(traj_path))

# Converts a CIF/PDB and .XTC file to a directory of PDBs
def export_frames_from_traj(self: Any) -> None:  # noqa: PLR0911
    """
    Exports each frame of the loaded trajectory as a separate PDB file.
    Prompts the user for confirmation and an output directory.

    Args:
        self: The main GUI class instance.
    """
    try:
        mol = getattr(self, "traj_mol_path", None)
        traj = getattr(self, "traj_xtc_path", None)
        if not mol or not traj:
            self.traj_status_label.setText("Please select both a PDB and a trajectory file.")
            return
        protein_name = getattr(self, "protein_name", None)
        if not isinstance(protein_name, str) or not object_exists(protein_name):
            self.traj_status_label.setText("The loaded molecule is no longer available in PyMOL.")
            return
        if not selection_has_atoms(object_selection(protein_name)):
            self.traj_status_label.setText("The loaded molecule selection has no atoms to export.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Export",
            "Are you sure you want to export all frames?\n\nThis will create a large number of PDB files!",
            QMessageBox.Yes | QMessageBox.No,
        )

        if confirm != QMessageBox.Yes:
            self.traj_status_label.setText("Export cancelled.")
            return

        outdir = QFileDialog.getExistingDirectory(self, "Select folder to save frames in the widget above")
        if not outdir:
            return

        outdir_path = resolve_output_path(self, outdir)
        if outdir_path is None:
            return
        start = 1
        end = cmd.count_states(object_selection(protein_name))
        if end < 1:
            self.traj_status_label.setText("The loaded molecule has no trajectory states to export.")
            return
        num_digits = len(str(end))

        for s in range(start, end + 1):
            cmd.frame(s)
            fname = outdir_path / f"frame_{s:0{num_digits}d}.pdb"
            cmd.save(str(fname), selection=object_selection(protein_name))

        self.selected_traj_dir_multi = outdir_path
        logger.info("%s frames were saved to %s", end, outdir_path)
        self.traj_status_label.setText(f"Exported {end} frames to {outdir_path}")
        self.update_list()

        mol_files = list_structure_files(outdir_path)
        self.avail_dir_traj_files = mol_files
        set_frame_spinbox_bounds(self.frame_selector_spinbox, len(mol_files))


    except Exception as e:
        logger.exception("Error exporting frames")
        self.traj_status_label.setText(f"Error: {e!s}")
