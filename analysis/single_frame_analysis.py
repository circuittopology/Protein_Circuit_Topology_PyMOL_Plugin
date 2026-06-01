import logging
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
from utils.helpers import resolve_output_path, temp_pdb_export
from utils.non_polymer import has_non_polymer_atoms
from utils.validation import (
    chain_selection,
    get_object_chains,
    legalize_object_name,
    list_structure_files,
    object_exists,
    selected_frame_file,
    selection_has_atoms,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def run_single_frame_analysis(self: Any) -> None:  # noqa: PLR0911, PLR0912, PLR0915
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

    circuit_plot_enabled = vals["circuit_plot"]
    matrix_plot_enabled = vals["matrix_plot"]
    stats_plot_enabled = vals["stats_plot"]
    export_cmap3_enabled = vals["export_cmap3"]
    export_mat_enabled = vals["export_mat"]

    if not circuit_plot_enabled and not matrix_plot_enabled and not export_cmap3_enabled and not export_mat_enabled and not stats_plot_enabled:
        QMessageBox.warning(self, "Error", "No checkboxes for plotting or exporting have been ticked!")
        return

    if traj_dir:
        source_dir = Path(traj_dir)
        frame_files = [Path(file_path) for file_path in getattr(self, "avail_dir_traj_files", [])]
    elif pdb_dir:
        source_dir = Path(pdb_dir)
        try:
            frame_files = list_structure_files(source_dir)
            self.available_mol_files = frame_files
        except Exception as e:  # noqa: BLE001
            QMessageBox.critical(self, "Error", f"Failed to read input directory:\n{e}")
            return
    else:
        QMessageBox.critical(self, "Error", "No input source selected (trajectory or directory).")
        return

    if not frame_files:
        QMessageBox.critical(self, "Error", "No PDB or CIF files are available for frame analysis.")
        return

    normalized_files = [file_path if file_path.is_absolute() else source_dir / file_path for file_path in frame_files]
    frame_idx = self.frame_selector_spinbox.value()
    try:
        full_path = selected_frame_file(normalized_files, frame_idx)
    except Exception as e:  # noqa: BLE001
        QMessageBox.critical(self, "Error", str(e))
        return

    output_path = None
    if export_cmap3_enabled or export_mat_enabled:
        output_path = resolve_output_path(self, vals["output_directory"])
        if output_path is None:
            return

    frame_dist = vals["cutoff_distance"]
    frame_numcontacts = vals["cutoff_numcontacts"]
    frame_neighbour = vals["exclude_neighbour"]
    loaded_frame_obj = None

    try:
        if traj_dir:
            frame_obj = getattr(self, "protein_name", None)
            if not isinstance(frame_obj, str) or not object_exists(frame_obj):
                msg = "The trajectory molecule is no longer available in PyMOL."
                raise RuntimeError(msg)  # noqa: TRY301
            cmd.set("state", frame_idx, frame_obj)
            traj_frame_chains = get_object_chains(frame_obj)
            frame_chain, protid = retrieve_chain(full_path)
        else:
            frame_obj = legalize_object_name(full_path.stem)
            cmd.load(str(full_path), frame_obj)
            loaded_frame_obj = frame_obj
            if not object_exists(frame_obj):
                msg = f"PyMOL did not create the expected object: {frame_obj}"
                raise RuntimeError(msg)  # noqa: TRY301
            traj_frame_chains = get_object_chains(frame_obj)
            frame_chain, protid = retrieve_chain(full_path)

        if not traj_frame_chains:
            msg = "No protein chains were found for the selected frame."
            raise ValueError(msg)  # noqa: TRY301

        if len(traj_frame_chains) > 1:
            frame_level = "model"
            logger.info("This trajectory object has multiple chains. Performing multi-chain CT analysis...")
        else:
            frame_level = "chain"

        idx, numbering, protid, _ = get_cmap(
            frame_chain,
            level=frame_level,
            cutoff_distance=frame_dist,
            cutoff_numcontacts=frame_numcontacts,
            exclude_neighbour=frame_neighbour,
        )
        if idx.size == 0:
            QMessageBox.warning(self, "Warning", "No residue contacts were found for the selected frame.")
            return

        if frame_level == "chain":
            mat, frame_psc, _ = get_matrix(idx, protid)
        else:
            mat, frame_psc, _ = get_matrix(index=idx, protid=protid)

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
                current_selection = chain_selection(frame_obj, c)
                if not selection_has_atoms(current_selection):
                    logger.warning("Skipping empty chain selection: %s", current_selection)
                    continue
                with temp_pdb_export(current_selection, state=cmd.get_state()) as tmp_path:
                    curr_chain, _ = retrieve_chain(tmp_path)
                temp_idx, temp_n, _, _ = get_cmap(
                    curr_chain,
                    cutoff_distance=frame_dist,
                    cutoff_numcontacts=frame_numcontacts,
                    exclude_neighbour=frame_neighbour,
                )
                if temp_idx.size == 0:
                    logger.warning("No contacts found for frame chain %s; skipping contact-map export", c)
                    continue
                cmap3_exports.append((temp_idx, f"{frame_obj}_chain_{c}", temp_n))

        if export_cmap3_enabled or export_mat_enabled:
            if output_path is None:
                return
            for temp_idx, chain_label, temp_n in cmap3_exports:
                export_cmap3(temp_idx, chain_label, temp_n, output_path)
            if export_mat_enabled:
                export_mat(idx, mat, frame_obj, output_path)
    except Exception as e:
        logger.exception("Single-frame analysis failed")
        QMessageBox.warning(self, "Error", f"Single-frame analysis failed:\n{e}")
    finally:
        if loaded_frame_obj and object_exists(loaded_frame_obj):
            cmd.delete(loaded_frame_obj)

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
