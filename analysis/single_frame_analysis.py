import logging
import tempfile
from pathlib import Path
from typing import Any

from pymol import cmd
from PyQt5.QtWidgets import QMessageBox

from functions.calculating.get_cmap import get_cmap
from functions.calculating.get_matrix import get_matrix
from functions.calculating.get_stats import get_stats
from functions.exporting.export_cmap3 import export_cmap3
from functions.exporting.export_mat import export_mat
from functions.importing.retrieve_chain import retrieve_chain
from functions.plots.circuit_plot import circuit_plot
from functions.plots.matrix_plot import matrix_plot
from functions.plots.matrix_plot_model import matrix_plot_model
from functions.plots.stats_plot import stats_plot
from utils.helpers import resolve_output_path
from utils.non_polymer import has_non_polymer_atoms

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def run_single_frame_analysis(self: Any) -> None:  # noqa: PLR0912, PLR0915
    """
    Runs circuit topology analysis for a single frame of a trajectory or a single PDB file from a directory.

    Args:
        self: The main GUI class instance.
    """
    # check for non-polymer atoms
    if has_non_polymer_atoms():
        QMessageBox.warning(self, "Warning",
                                        "The opened file contains non-polymer atoms, which can interfere with Circuit Topology. Please use the 'Remove Non-Polymer Atoms' button to remove them.")

    vals = self.get_multiple_values()

    traj_dir = vals.get("traj_directory")
    pdb_dir = vals.get("directory")

    # Check for missing or empty file lists
    if traj_dir:
        if not hasattr(self, "avail_dir_traj_files") or not self.avail_dir_traj_files:
            QMessageBox.critical(self, "Error", "No trajectory files found in the selected trajectory directory.")
            return
    elif pdb_dir:
        if not hasattr(self, "available_mol_files") or not self.available_mol_files:
            QMessageBox.critical(self, "Error", "No PDB files found in the selected directory.")
            return
    else:
        QMessageBox.critical(self, "Error", "No input source selected (trajectory or directory).")
        return


    circuit_plot_enabled = vals["circuit_plot"]
    matrix_plot_enabled = vals["matrix_plot"]
    stats_plot_enabled = vals["stats_plot"]
    export_cmap3_enabled = vals["export_cmap3"]
    export_mat_enabled = vals["export_mat"]

    # Check to see if GUI has at least one checkbox ticked for the 'run analysis' part
    if not circuit_plot_enabled and not matrix_plot_enabled and not export_cmap3_enabled and not export_mat_enabled and not stats_plot_enabled:
        QMessageBox.warning(self, "Error", "No checkboxes for plotting or exporting have been ticked!")
        return

    # Correctly retrieve the frame
    if vals["traj_directory"]:
        file_directory = vals["traj_directory"]
        frame_idx = self.frame_selector_spinbox.value()
        selected_file = Path(self.avail_dir_traj_files[frame_idx - 1])
        full_path = Path(file_directory) / selected_file
        frame_obj = self.protein_name
        cmd.set("state", frame_idx, frame_obj)
        traj_frame_chains = cmd.get_chains(frame_obj)
        frame_chain, protid = retrieve_chain(full_path)
    else:
        file_directory = vals["directory"]
        frame_idx = self.frame_selector_spinbox.value()
        selected_file = Path(self.available_mol_files[frame_idx - 1])
        full_path = Path(file_directory) / selected_file
        frame_obj = full_path.stem
        cmd.load(full_path, frame_obj)
        traj_frame_chains = cmd.get_chains(frame_obj)
        frame_chain, protid = retrieve_chain(full_path)

    frame_dist = vals["cutoff_distance"]
    frame_numcontacts = vals["cutoff_numcontacts"]
    frame_neighbour = vals["exclude_neighbour"]

    frame_output_directory = vals["output_directory"]

    if not frame_output_directory and (export_cmap3_enabled or export_mat_enabled):
        QMessageBox.warning(self, "Error", "An output directory has not been selected.")
        return

    if len(traj_frame_chains) > 1:
        frame_level = "model"
        logger.info("This trajectory object has multiple chains. Performing multi-chain CT analysis...")
    else:
        frame_level = "chain"

    idx, numbering, protid, _ = get_cmap(frame_chain, level=frame_level, cutoff_distance=frame_dist,
                                                    cutoff_numcontacts=frame_numcontacts,
                                                    exclude_neighbour=frame_neighbour)

    # matrix retrieval (depends on object level 'chain' vs 'model' (single- vs multi-chain))
    if frame_level == "chain":
        mat, frame_psc, _ = get_matrix(idx, protid)
    else:
        mat, frame_psc, _ = get_matrix(index=idx, protid=protid)

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
        stats_plot(entangled, frame_psc, protid)

    cmap3_exports = []
    if export_cmap3_enabled:
        for c in traj_frame_chains:
            with tempfile.NamedTemporaryFile(suffix=".pdb", delete=False) as tmp:
                tmp_path = Path(tmp.name)
            cmd.save(tmp_path, f"{frame_obj} and chain {c}", state=cmd.get_state())
            try:
                curr_chain, _ = retrieve_chain(tmp_path)
                temp_idx, temp_n, _, _ = get_cmap(curr_chain, cutoff_distance=frame_dist,
                                                            cutoff_numcontacts=frame_numcontacts,
                                                            exclude_neighbour=frame_neighbour)
                cmap3_exports.append((temp_idx, f"{frame_obj}_chain_{c}", temp_n))
            finally:
                if tmp_path.exists():
                    tmp_path.unlink()

    if export_cmap3_enabled or export_mat_enabled:
        output_path = resolve_output_path(self, frame_output_directory)
        if output_path is None:
            return
        for temp_idx, chain_label, temp_n in cmap3_exports:
            export_cmap3(temp_idx, chain_label, temp_n, output_path)
        if export_mat_enabled:
            export_mat(idx, mat, frame_obj, output_path)

    # If we are processing a trajectory that was imported as a directory of PDBs, then we first loaded the corresponding frame to retrieve chain info about it
    # and now that we are done, we can remove it
    if vals["directory"]:
        cmd.delete(frame_obj)

# Enables single frame analysis based on the checkbox
def toggle_frame_controls(self: Any, enabled: bool) -> None:
    """
    Toggles the enabled state of the frame selector and run button.

    Args:
        self: The main GUI class instance.
        enabled (bool): True to enable, False to disable.
    """
    self.frame_selector_spinbox.setEnabled(enabled)
    self.run_single_frame_button.setEnabled(enabled)
