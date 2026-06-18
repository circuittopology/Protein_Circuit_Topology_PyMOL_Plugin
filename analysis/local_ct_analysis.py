import logging
from typing import Any

import numpy as np
from pymol import cmd
from PyQt5.QtWidgets import QMessageBox

from functions.calculating.get_cmap import get_cmap
from functions.calculating.get_matrix import get_matrix
from functions.calculating.local_ct import local_ct
from functions.exporting.export_cmap3 import export_cmap3
from functions.exporting.export_mat import export_mat
from functions.importing.retrieve_chain import retrieve_chain
from functions.plots.local_topology_plot import local_topology_plot
from utils.config import CHECKBOX_WARN, LOCAL_CT_WARN, WARN_MSG
from utils.helpers import resolve_output_path, temp_pdb_export
from utils.non_polymer import has_non_polymer_atoms
from utils.validation import chain_selection, get_object_chains, object_exists, selection_has_atoms

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def run_local_ct(self: Any) -> None:  # noqa: PLR0911, PLR0912, PLR0915
    """
    Runs the local circuit topology analysis based on user-selected parameters.
    Handles data retrieval, calculation, plotting, and exporting.

    Args:
        self: The main GUI class instance.
    """
    # check for non-polymer atoms
    if has_non_polymer_atoms():
        QMessageBox.warning(self, "Warning", WARN_MSG)

    vals = self.get_local_values()
    # Retrieve imported file as a selected object in PyMOL
    curr_local_obj = self.local_dropdown_objects.currentText()
    curr_chain = self.chain_combo_box.currentText()

    if not object_exists(curr_local_obj):
        QMessageBox.warning(self, "Error", LOCAL_CT_WARN)
        return
    chains = get_object_chains(curr_local_obj)
    if not curr_chain or curr_chain not in chains:
        QMessageBox.warning(self, "Error", "Please select a valid chain for local Circuit Topology analysis.")
        return

    selected_obj = chain_selection(curr_local_obj, curr_chain)
    if not selection_has_atoms(selected_obj):
        QMessageBox.warning(self, "Error", "The selected object/chain has no atoms to analyze.")
        return

    local_ct_plot = vals["local_topology_plot"]
    selected_residue_id = vals["res_id"]
    contact = vals["contact_type"]
    local_ct_enabled = vals["local_ct"]
    export_cmap3_enabled = vals["export_cmap3"]
    export_mat_enabled = vals["export_mat"]

    # Check to see if GUI has at least one checkbox ticked for the 'run analysis' part
    if not (local_ct_plot or local_ct_enabled or export_cmap3_enabled or export_mat_enabled):
        QMessageBox.warning(self, "Error", CHECKBOX_WARN)
        return

    output_path = None
    if export_cmap3_enabled or export_mat_enabled:
        output_path = resolve_output_path(self, vals["output_directory"])
        if output_path is None:
            return

    local_dist = vals["cutoff_distance"]
    local_numcontacts = vals["cutoff_numcontacts"]
    local_neighbour = vals["exclude_neighbour"]
    base_file_typeless = f"{curr_local_obj}_chain_{curr_chain}"
    try:
        with temp_pdb_export(selected_obj, state=cmd.get_state()) as tmp_path:
            local_chain, protid = retrieve_chain(tmp_path)
    except Exception as e:
        logger.exception("Failed to export or parse local selection: %s", selected_obj)
        QMessageBox.warning(self, "Error", f"Failed to prepare the selected chain for local analysis:\n{e}")
        return

    try:
        idx, numbering, protid, _ = get_cmap(
            chain=local_chain,
            cutoff_distance=local_dist,
            cutoff_numcontacts=local_numcontacts,
            exclude_neighbour=local_neighbour,
        )
        if idx.size == 0:
            QMessageBox.warning(self, "Warning", "No residue contacts were found with the current parameters.")
            return
        matches = np.where(np.asarray(numbering) == selected_residue_id)[0]
        if len(matches) == 0:
            QMessageBox.warning(self, "Error", f"Residue {selected_residue_id} was not found in the selected chain.")
            return
        residue_id = int(matches[0])
        mat, _, _ = get_matrix(idx, protid)
    except Exception as e:
        logger.exception("Local CT analysis failed for %s", selected_obj)
        QMessageBox.warning(self, "Error", f"Local analysis failed:\n{e}")
        return

    try:
        if local_ct_plot:
            local_topology_plot(idx, mat, numbering, residue_id, contact)
        if local_ct_enabled:
            logger.info(local_ct(idx, mat, numbering))
    except Exception as e:
        logger.exception("Local CT output failed for %s", selected_obj)
        QMessageBox.warning(self, "Error", f"Local CT output failed:\n{e}")
        return

    if export_cmap3_enabled or export_mat_enabled:
        if output_path is None:
            return
        try:
            if export_cmap3_enabled:
                export_cmap3(idx, base_file_typeless, numbering, output_path)
            if export_mat_enabled:
                export_mat(idx, mat, base_file_typeless, output_path)
        except Exception as e:
            logger.exception("Local CT export failed for %s", selected_obj)
            QMessageBox.warning(self, "Error", f"Local export failed:\n{e}")
