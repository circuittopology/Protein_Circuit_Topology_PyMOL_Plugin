"""
Utility functions for handling trajectory files in the PyMOL plugin.
"""
import logging
from pathlib import Path
from typing import Any

from pymol import cmd
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from utils.non_polymer import remove_non_polymer_atoms

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
        self.traj_mol_path = fname
        self.traj_mol_label.setText(fname)
        fname_path = Path(fname)
        mol_name = fname_path.stem
        cmd.load(fname, mol_name)
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
        self.traj_xtc_path = fname
        self.traj_xtc_label.setText(fname)
        # If the trajectory is imported into the GUI, load it into PyMOL first
        cmd.load_traj(fname, object=self.protein_name, state=1)
        remove_non_polymer_atoms()

# Converts a CIF/PDB and .XTC file to a directory of PDBs
def export_frames_from_traj(self: Any) -> None:
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

        outdir_path = Path(outdir)
        start = 1
        end = cmd.count_states(self.protein_name)
        num_digits = len(str(end))

        for s in range(start, end + 1):
            cmd.frame(s)
            fname = outdir_path / f"frame_{s:0{num_digits}d}.pdb"
            cmd.save(str(fname), selection=self.protein_name)

        self.selected_traj_dir_multi = outdir
        logger.info("%s frames were saved to %s", end, outdir)
        self.traj_status_label.setText(f"Exported {end} frames to {outdir}")
        self.update_list()

        mol_files = sorted([f for f in outdir_path.iterdir() if f.suffix == ".pdb"])
        self.avail_dir_traj_files = mol_files
        self.frame_selector_spinbox.setMaximum(len(mol_files))


    except Exception as e:
        logger.exception("Error exporting frames")
        self.traj_status_label.setText(f"Error: {e!s}")
