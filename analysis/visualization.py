import logging
from typing import Any

from pymol import cmd
from PyQt5.QtWidgets import QMessageBox

from functions.calculating.get_cmap import get_cmap
from functions.calculating.get_matrix import get_matrix
from functions.importing.retrieve_chain import retrieve_chain
from utils.helpers import temp_pdb_export
from utils.topology import color_by_topology, get_topology_vector
from utils.validation import chain_selection, get_object_chains, object_exists, selection_has_atoms

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Function that only visualizes the topology on the molecule inside PyMOL
def visualize_molecule(self: Any, contact_type: str) -> None:
    """
    Visualizes the circuit topology on the selected molecule in PyMOL by coloring residues based on contact density.

    Args:
        self: The main GUI class instance.
        contact_type (str): The type of contact to visualize ('P', 'S', 'X').
    """
    vals = self.get_vis_vals()

    # Only supported for an object already inside PyMOL
    selected_obj = self.dropdown_objects.currentText()

    if not object_exists(selected_obj):
        QMessageBox.warning(self, "Error",
                                        "Please select an object inside PyMOL for the Circuit Topology analysis!")
        return

    chains = get_object_chains(selected_obj)
    if not chains:
        QMessageBox.warning(self, "Error", f"No protein chains were found for object: {selected_obj}")
        return
    logger.info("Chains found: %s", chains)

    for chain_id in chains:
        current_selection = chain_selection(selected_obj, chain_id)
        if not selection_has_atoms(current_selection):
            logger.warning("Skipping empty chain selection: %s", current_selection)
            continue

        try:
            vis_dist = vals["cutoff_distance"]
            vis_numcontacts = vals["cutoff_numcontacts"]
            vis_neighbour = vals["exclude_neighbour"]
            with temp_pdb_export(current_selection, state=cmd.get_state()) as tmp_path:
                visual_chain, protid = retrieve_chain(tmp_path)

            idx, numbering, protid, _ = get_cmap(
                visual_chain,
                cutoff_distance=vis_dist,
                cutoff_numcontacts=vis_numcontacts,
                exclude_neighbour=vis_neighbour,
            )
            if idx.size == 0:
                logger.warning("No contacts found for chain %s. Skipping visualization...", chain_id)
                continue
            mat, psc, _ = get_matrix(idx, protid)
            if psc == [protid, 0, 0, 0]:
                logger.warning(
                    "Cannot create topology matrix for chain %s, so visualization for this chain cannot be performed!", chain_id)
                continue
            logger.info("Coloring object based on chain %s ...", chain_id)
            top_vec = get_topology_vector(mat=mat, index=idx, topology_type=contact_type, numbering=numbering)
            if top_vec is None:
                logger.warning("Invalid contact type for chain %s. Skipping visualization...", chain_id)
                continue
            color_by_topology(
                molecule_name=selected_obj,
                topology_vector=top_vec,
                numbering=numbering,
                topology_type=contact_type,
            )
        except Exception as e:
            logger.exception("Visualization failed for chain %s", chain_id)
            QMessageBox.warning(self, "Error", f"Visualization failed for chain {chain_id}:\n{e}")
            return
