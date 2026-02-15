"""
Utility functions for handling trajectory files in the PyMOL plugin.
"""
import os
import sys
from pathlib import Path
from pymol import cmd
from pymol.Qt import QtWidgets
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
# pylint: disable=wrong-import-position
from utils.non_polymer import remove_non_polymer_atoms

def select_mol_file(self):
    """
    Gets the trajectory corresponding molecule file (PDB)

    Note: CIF files are generally not used for trajectory analysis in PyMOL.
    """
    fname, _ = QtWidgets.QFileDialog.getOpenFileName(
        self,
        "Select PDB file",
        "",
        "Structure files (*.pdb)"
    )
    if fname:
        self.traj_mol_path = fname
        self.traj_mol_label.setText(fname)
        # If the molecule is imported into the GUI, load it into PyMOL first
        mol_name = os.path.splitext(os.path.basename(fname))[0]
        cmd.load(fname, mol_name)
        self.protein_name = mol_name

# Gets the trajectory file
def select_xtc_file(self):
    """
    Gets the trajectory file (XTC/DCD/TRR/NC)
    """
    fname, _ = QtWidgets.QFileDialog.getOpenFileName(
        self,
        "Select trajectory file",
        "",
        "Trajectory files (*.xtc *.dcd *.trr *.nc)"
    )
    if fname:
        self.traj_xtc_path = fname
        self.traj_xtc_label.setText(fname)
        # If the trajectory is imported into the GUI, load it into PyMOL first
        cmd.load_traj(fname, object=self.protein_name, state=1)
        remove_non_polymer_atoms()

def export_frames_from_traj(self):
    """
    Exports all frames from the molecule trajectory as individual PDB files in a selected directory.
    """
    try:
        mol = getattr(self, 'traj_mol_path', None)
        traj = getattr(self, 'traj_xtc_path', None)
        if not mol or not traj:
            self.traj_status_label.setText("Please select both a PDB and a trajectory file.")
            return

        confirm = QtWidgets.QMessageBox.question(
            self,
            "Confirm Export",
            "Are you sure you want to export all frames?\n\nThis will create a large number of PDB files!",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if confirm != QtWidgets.QMessageBox.Yes:
            self.traj_status_label.setText("Export cancelled.")
            return

        outdir = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select folder to save frames in the widget above"
        )
        if not outdir:
            return

        start = 1
        end = cmd.count_states(self.protein_name)
        num_digits = len(str(end))

        for s in range(start, end + 1):
            cmd.frame(s)
            fname = os.path.join(outdir, f"frame_{s:0{num_digits}d}.pdb")
            cmd.save(fname, selection=self.protein_name)

        self.selected_traj_dir_multi = outdir
        print(f"{end} frames were saved to {outdir}")
        self.traj_status_label.setText(f"Exported {end} frames to {outdir}")
        self.update_list()

        mol_files = sorted([f for f in os.listdir(outdir) if f.endswith(".pdb")])
        self.avail_dir_traj_files = mol_files
        self.frame_selector_spinbox.setMaximum(len(mol_files))


    except Exception as e:
        self.traj_status_label.setText(f"Error: {str(e)}")
