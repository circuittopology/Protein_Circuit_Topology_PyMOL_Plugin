import os
from typing import Any

from pymol import cmd
from PyQt5.QtWidgets import QMessageBox

from functions.calculating.get_cmap import get_cmap
from functions.calculating.get_matrix import get_matrix

from functions.importing.retrieve_chain import retrieve_chain

from utils.topology import get_topology_vector, color_by_topology


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

    if selected_obj == "Select a file." or not selected_obj:
        QMessageBox.warning(self, "Error",
                                        "Please select an object inside PyMOL for the Circuit Topology analysis!")
        return

    if selected_obj != "Select a file.":  # If the object is inside PyMOL
        chains = cmd.get_chains(selected_obj)
        print("Chains found: ", chains)

        for chain_id in chains:
            file_name = f"{selected_obj}_chain_{chain_id}_export.pdb"
            cmd.save(file_name, f"{selected_obj} and chain {chain_id}", state=cmd.get_state())

            vis_dist = vals["cutoff_distance"]
            vis_numcontacts = vals["cutoff_numcontacts"]
            vis_neighbour = vals["exclude_neighbour"]
            visual_chain, protid = retrieve_chain(file_name)

            idx, numbering, protid, _ = get_cmap(visual_chain, cutoff_distance=vis_dist,
                                                            cutoff_numcontacts=vis_numcontacts,
                                                            exclude_neighbour=vis_neighbour)
            mat, psc, _ = get_matrix(idx, protid)
            if psc == [protid, 0, 0, 0]:
                print(
                    f"Cannot create topology matrix for chain {chain_id}, so visualization for this chain cannot be performed!")
                if os.path.exists(file_name):
                    os.remove(os.path.abspath(file_name))
                continue
            print(f"Coloring object based on chain {chain_id} ...")
            top_vec = get_topology_vector(mat=mat, index=idx, topology_type=contact_type, numbering=numbering)
            if top_vec is None:
                print(f"Invalid contact type for chain {chain_id}. Skipping visualization...")
                if os.path.exists(file_name):
                    os.remove(os.path.abspath(file_name))
                continue
            color_by_topology(molecule_name=selected_obj, topology_vector=top_vec, numbering=numbering,
                                topology_type=contact_type)

            if os.path.exists(file_name):
                os.remove(os.path.abspath(file_name))
