import logging
from typing import Any

from pymol import cmd
from PyQt5.QtWidgets import QMessageBox

from functions.calculating.get_cmap import get_cmap
from functions.calculating.get_matrix import get_matrix
from functions.importing.retrieve_chain import retrieve_chain
from utils.helpers import temp_pdb_export
from utils.topology import color_by_topology, get_topology_vector
from utils.validation import (
    chain_selection,
    count_object_states,
    get_object_chains,
    object_exists,
    selection_has_atoms,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def _safe_delete(*names: str) -> None:
    """Delete PyMOL objects/selections, ignoring names that do not exist."""
    for name in names:
        try:
            cmd.delete(name)
        except Exception:  # noqa: BLE001, PERF203
            logger.debug("Cleanup delete failed for %s", name, exc_info=True)


def _color_chains_by_topology(target_obj: str, contact_type: str, vals: dict[str, Any], state: int) -> int:
    """
    Colors each chain of a single-state object by its circuit topology.

    Args:
        target_obj (str): Name of the PyMOL object to color.
        contact_type (str): The type of contact to visualize ('P', 'S', 'X').
        vals (dict): Visualization parameters from ``get_vis_vals``.
        state (int): The coordinate state to export and analyze.

    Returns:
        int: The number of chains that were successfully colored.
    """
    vis_dist = vals["cutoff_distance"]
    vis_numcontacts = vals["cutoff_numcontacts"]
    vis_neighbour = vals["exclude_neighbour"]

    colored = 0
    for chain_id in get_object_chains(target_obj):
        current_selection = chain_selection(target_obj, chain_id)
        if not selection_has_atoms(current_selection):
            logger.warning("Skipping empty chain selection: %s", current_selection)
            continue

        with temp_pdb_export(current_selection, state=state) as tmp_path:
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
        logger.info("Coloring %s based on chain %s ...", target_obj, chain_id)
        top_vec = get_topology_vector(mat=mat, index=idx, topology_type=contact_type, numbering=numbering)
        if top_vec is None:
            logger.warning("Invalid contact type for chain %s. Skipping visualization...", chain_id)
            continue
        color_by_topology(
            molecule_name=target_obj,
            topology_vector=top_vec,
            numbering=numbering,
            topology_type=contact_type,
        )
        colored += 1
    return colored


def _visualize_trajectory(self: Any, contact_type: str, selected_obj: str, vals: dict[str, Any], n_states: int) -> None:
    """
    Colors every state of a trajectory object by its own circuit topology.

    Args:
        self: The main GUI class instance (used as the dialog parent).
        contact_type (str): The type of contact to visualize ('P', 'S', 'X').
        selected_obj (str): Name of the trajectory object.
        vals (dict): Visualization parameters from ``get_vis_vals``.
        n_states (int): Number of states in ``selected_obj``.
    """
    confirm = QMessageBox.question(
        self,
        "Color all trajectory states?",
        (
            f"'{selected_obj}' is a trajectory with {n_states} states.\n\n"
            f"Coloring it runs the full Circuit Topology analysis for every state and chain, "
            f"colors each frame by its own {contact_type} topology.\n\n"
            f"This may take a while and use significant memory for long trajectories. Continue?"
        ),
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No,
    )
    if confirm != QMessageBox.Yes:
        logger.info("Trajectory coloring cancelled by user.")
        return

    result_obj = f"{selected_obj}_topo"
    split_prefix = f"{selected_obj}_ct_"
    _safe_delete(f"{split_prefix}*", result_obj)
    before = set(cmd.get_object_list())

    try:
        cmd.split_states(selected_obj, prefix=split_prefix)
    except Exception as e:
        logger.exception("Failed to split trajectory %s into per-state objects", selected_obj)
        QMessageBox.warning(self, "Error", f"Failed to split the trajectory into states:\n{e}")
        return
    state_objs = sorted(set(cmd.get_object_list()) - before)
    if not state_objs:
        QMessageBox.warning(self, "Error", "Splitting the trajectory produced no per-state objects.")
        return

    colored_states = 0
    for state_obj in state_objs:
        try:
            if _color_chains_by_topology(state_obj, contact_type, vals, state=1) > 0:
                colored_states += 1
        except Exception:  # noqa: PERF203
            logger.exception("Failed to color state object %s; skipping it.", state_obj)

    if colored_states == 0:
        _safe_delete(f"{split_prefix}*")
        QMessageBox.warning(
            self, "Warning",
            "No states could be colored. No residue contacts were found with the current parameters.",
        )
        return

    try:
        cmd.join_states(result_obj, f"{split_prefix}*", mode=0)
        if not object_exists(result_obj) or count_object_states(result_obj) < 1:
            msg = "join_states did not produce a multi-state object"
            raise RuntimeError(msg)  # noqa: TRY301
    except Exception:
        logger.exception("join_states failed; falling back to coloring the current state only.")
        _safe_delete(result_obj, f"{split_prefix}*")
        QMessageBox.warning(
            self, "Falling back to current state",
            (
                f"The colored states could not be merged into a single object on this PyMOL build, "
                f"so only the current state of '{selected_obj}' will be colored by {contact_type} topology."
            ),
        )
        try:
            _color_chains_by_topology(selected_obj, contact_type, vals, state=cmd.get_state())
        except Exception as e:
            logger.exception("Fallback current-state coloring failed for %s", selected_obj)
            QMessageBox.warning(self, "Error", f"Visualization failed:\n{e}")
        return

    _safe_delete(f"{split_prefix}*")
    cmd.disable(selected_obj)
    cmd.set("all_states", 0)
    cmd.frame(1)

    logger.info("Colored %s/%s states; created scrubbable object '%s'.", colored_states, len(state_objs), result_obj)
    QMessageBox.information(
        self, "Done",
        (
            f"Colored {colored_states} of {len(state_objs)} states by {contact_type} topology.\n\n"
            f"Created '{result_obj}'. The original '{selected_obj}' has been hidden. Delete '{result_obj}' to clean up."
        ),
    )


# Function that only visualizes the topology on the molecule inside PyMOL
def visualize_molecule(self: Any, contact_type: str) -> None:
    """
    Visualizes the circuit topology on the selected molecule in PyMOL by coloring residues based on contact density.

    Args:
        self: The main GUI class instance.
        contact_type (str): The type of contact to visualize ('P', 'S', 'X').
    """
    vals = self.get_vis_vals()
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

    n_states = count_object_states(selected_obj)
    if n_states > 1:
        _visualize_trajectory(self, contact_type, selected_obj, vals, n_states)
        return

    try:
        _color_chains_by_topology(selected_obj, contact_type, vals, state=cmd.get_state())
    except Exception as e:
        logger.exception("Visualization failed for %s", selected_obj)
        QMessageBox.warning(self, "Error", f"Visualization failed:\n{e}")
