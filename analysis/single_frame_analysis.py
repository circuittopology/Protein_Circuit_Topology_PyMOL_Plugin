import sys
from pathlib import Path
import os

from pymol import cmd
from pymol.Qt import QtWidgets
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
# pylint: disable=wrong-import-position
from functions.calculating.get_cmap import get_cmap
from functions.calculating.get_matrix import get_matrix
from functions.calculating.get_stats import get_stats

from functions.importing.retrieve_chain import retrieve_chain

from functions.plots.circuit_plot import circuit_plot
from functions.plots.matrix_plot import matrix_plot
from functions.plots.stats_plot import stats_plot
from functions.plots.matrix_plot_model import matrix_plot_model

from functions.exporting.export_cmap3 import export_cmap3
from functions.exporting.export_mat import export_mat

from utils.non_polymer import has_non_polymer_atoms

# Another version of an analysis, this one is for a single frame. Eventually we should combine all analysis types into one function to make it nicer
def run_single_frame_analysis(self):
    # check for non-polymer atoms
    if has_non_polymer_atoms():
        QtWidgets.QMessageBox.warning(self, "Warning",
                                        "The opened file contains non-polymer atoms, which can interfere with Circuit Topology. Please use the 'Remove Non-Polymer Atoms' button to remove them.")

    vals = self.get_multiple_values()

    traj_dir = vals.get("traj_directory")
    pdb_dir = vals.get("directory")

    # Check for missing or empty file lists
    if traj_dir:
        if not hasattr(self, "avail_dir_traj_files") or not self.avail_dir_traj_files:
            QtWidgets.QMessageBox.critical(self, "Error", "No trajectory files found in the selected trajectory directory.")
            return
    elif pdb_dir:
        if not hasattr(self, "available_mol_files") or not self.available_mol_files:
            QtWidgets.QMessageBox.critical(self, "Error", "No PDB files found in the selected directory.")
            return
    else:
        QtWidgets.QMessageBox.critical(self, "Error", "No input source selected (trajectory or directory).")
        return


    circuit_plot_enabled = vals["circuit_plot"]
    matrix_plot_enabled = vals["matrix_plot"]
    stats_plot_enabled = vals["stats_plot"]
    export_cmap3_enabled = vals["export_cmap3"]
    export_mat_enabled = vals["export_mat"]

    # Check to see if GUI has at least one checkbox ticked for the 'run analysis' part
    if not circuit_plot_enabled and not matrix_plot_enabled and not export_cmap3_enabled and not export_mat_enabled and not stats_plot_enabled:
        QtWidgets.QMessageBox.warning(self, "Error", "No checkboxes for plotting or exporting have been ticked!")
        return

    # Correctly retrieve the frame
    if vals["traj_directory"]:
        file_directory = vals['traj_directory']
        frame_idx = self.frame_selector_spinbox.value()
        selected_file = self.avail_dir_traj_files[frame_idx]
        full_path = os.path.join(file_directory, selected_file)
        frame_obj = self.protein_name
        cmd.set("state", frame_idx, frame_obj)
        traj_frame_chains = cmd.get_chains(frame_obj)
        frame_chain, protid = retrieve_chain(full_path)
    else:
        file_directory = vals['directory']
        frame_idx = self.frame_selector_spinbox.value()
        selected_file = self.available_mol_files[frame_idx]
        full_path = os.path.join(file_directory, selected_file)
        frame_obj = os.path.splitext(os.path.basename(full_path))[0]
        cmd.load(full_path, frame_obj)
        traj_frame_chains = cmd.get_chains(frame_obj)
        frame_chain, protid = retrieve_chain(full_path)

    frame_dist = vals["cutoff_distance"]
    frame_numcontacts = vals["cutoff_numcontacts"]
    frame_neighbour = vals["exclude_neighbour"]

    frame_output_directory = vals["output_directory"]

    if len(traj_frame_chains) > 1:
        frame_level = "model"
        print("This trajectory object has multiple chains. Performing multi-chain CT analysis...")
    else:
        frame_level = "chain"

    idx, numbering, protid, res_names = get_cmap(frame_chain, level=frame_level, cutoff_distance=frame_dist,
                                                    cutoff_numcontacts=frame_numcontacts,
                                                    exclude_neighbour=frame_neighbour)

    # matrix retrieval (depends on object level 'chain' vs 'model' (single- vs multi-chain))
    if frame_level == "chain":
        mat, psc = get_matrix(idx, protid)
    else:
        mat, frame_stats, frame_chain_stats = get_matrix(index=idx, protid=protid)

    # plotting
    if circuit_plot_enabled:
        circuit_plot(index=idx, protid=protid, numbering=numbering)
    if matrix_plot_enabled:
        if frame_level == "chain":
            matrix_plot(mat=mat, protid=protid)
        else:
            matrix_plot_model(mat=mat, protid=protid)
    
    if stats_plot_enabled:
        entangled = get_stats(mat=mat)
        if frame_level == "chain":
            stats_plot(entangled, psc, protid)
        else:
            stats_plot(entangled, frame_stats, protid)

    # csv exporting
    if export_cmap3_enabled:
        for c in traj_frame_chains:
            temp_file_name = f"{frame_obj}_chain_{c}_export.pdb"
            cmd.save(temp_file_name, f"{frame_obj} and chain {c}", state=cmd.get_state())
            temp_fpath = os.path.abspath(temp_file_name)
            curr_chain, p = retrieve_chain(temp_fpath)
            temp_idx, temp_n, p, res_names = get_cmap(curr_chain, cutoff_distance=frame_dist,
                                                        cutoff_numcontacts=frame_numcontacts,
                                                        exclude_neighbour=frame_neighbour)
            temp_file_base = os.path.basename(temp_fpath)
            typeless_temp_file = temp_file_base.split('.')[0]
            export_cmap3(temp_idx, typeless_temp_file, temp_n, frame_output_directory)
            if os.path.exists(temp_file_name):
                os.remove(temp_fpath)

    if export_mat_enabled:
        export_mat(idx, mat, frame_obj, frame_output_directory)

    # If we are processing a trajectory that was imported as a directory of PDBs, then we first loaded the corresponding frame to retrieve chain info about it
    # and now that we are done, we can remove it
    if vals["directory"]:
        cmd.delete(frame_obj)
        
# Enables single frame analysis based on the checkbox 
def toggle_frame_controls(self, enabled):
    self.frame_selector_spinbox.setEnabled(enabled)
    self.run_single_frame_button.setEnabled(enabled)