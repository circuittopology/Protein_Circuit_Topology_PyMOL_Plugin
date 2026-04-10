import logging
from typing import Any

from pymol import cmd, stored

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def get_residue_range(self: Any, obj_name: str | None) -> None:
    """
    Retrieves the residue range for each chain in the specified object.
    Updates the chain combo box and residue range spinbox.

    Args:
        self: The main GUI class instance.
        obj_name (str): The name of the object to analyze.
    """
    if not obj_name or obj_name == "Select a file.":
        return
    try:
        chains = cmd.get_chains(obj_name)
        self.curr_chain_residues = {}
        for c in chains:
            stored.resi_list = []
            cmd.iterate(f"{obj_name} and chain {c} and name CA",
                        "stored.resi_list.append(resv)")
            resi_list = stored.resi_list

            if resi_list:
                self.curr_chain_residues[c] = [min(resi_list), max(resi_list)]
            else:
                self.box_res_id.setRange(0, 0)
                self.box_res_id.setValue(0)

        self.update_chain_combo_box()

    except Exception:
        logger.exception("Error getting residue range")
        self.box_res_id.setRange(0, 0)
        self.box_res_id.setValue(0)

def update_residue_range(self: Any) -> None:
    """
    Updates the residue range spinbox based on the currently selected chain.

    Args:
        self: The main GUI class instance.
    """
    selected_chain = self.chain_combo_box.currentText()
    if not selected_chain:
        return
    try:
        min_resi, max_resi = self.curr_chain_residues[selected_chain]
        self.box_res_id.setRange(min_resi, max_resi)
        self.box_res_id.setValue(min_resi)
    except KeyError:
        pass
