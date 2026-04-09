from pymol import cmd
from typing import Any

import numpy as np

def get_topology_vector(mat: np.ndarray, index: np.ndarray, topology_type: str, numbering: np.ndarray) -> Any:
    """
    The get_topology_vector that Vasiliy provided that we modified to take the actual contact values
    instead of the indices when coloring.
    
    Args:
        mat: The topology matrix.
        index: The index array.
        topology_type: The type of topology ("P", "S", "X").
        numbering: Residue indexes from pdb or cif file.
        
    Returns:
        The calculated topology vector.
    """
    if topology_type == 'S':
        vec = np.sum((mat == 1), axis=1)
    elif topology_type == 'P':
        vec = np.sum(np.logical_or(mat == 2, mat == 3), axis=1)
    elif topology_type == 'X':
        vec = np.sum((mat == 4), axis=1)
    else:
        print("Please select a valid contact type!")
        return

    res1 = numbering[index[:, 0]]
    res2 = numbering[index[:, 1]]

    bins = np.linspace(np.min(numbering), np.max(numbering) + 1,
                       np.max(numbering) - np.min(numbering) + 2)
    count, _, __ = np.histogram2d(res1, res2, bins=(bins, bins), weights=vec)
    count = count + count.T - np.diag(np.diag(count))
    topology_vector = np.sum(count, axis=1)
    
    return topology_vector


def color_by_topology(molecule_name: str, topology_vector: np.ndarray, numbering: np.ndarray, topology_type: str) -> None:
    """
    Function that takes the topology vector from the get_topology_vector function and 
    recolors the selected PyMOL object based on the topology_type (e.g., 'P', 'S', 'X').
    
    Output is also printed (minimum and maximum contacts of topology_type) to inform the user
    of the color scheme.
    
    Args:
        molecule_name: The name of the molecule in PyMOL.
        topology_vector: The topology vector calculated previously.
        numbering: Residue numbering array.
        topology_type: The topology type used for coloring.
    """
    # Specify color palette for spectrum and colors for ramp
    if topology_type == "P":
        color_palette = "blue_red"
        colors = ["blue", "red"]
    elif topology_type == "S":
        color_palette = "cyan_yellow"
        colors = ["cyan", "yellow"]
    elif topology_type == "X":
        color_palette = "magenta_green"
        colors = ["magenta", "green"]
    else:
        print("Please select a valid contact type!")
        return

    topo_obj = molecule_name

    # color the clone
    residual_values = {str(res): float(val) for res, val in zip(numbering, topology_vector)}
    num_states = cmd.count_states(topo_obj)
    resi_list = "+".join(map(str, numbering))
    min_val, max_val = float(np.min(topology_vector)), float(np.max(topology_vector))
    print(f"Applying coloring to {num_states} states in {molecule_name}...")

    for state in range(1, num_states + 1):
        cmd.frame(state)

        cmd.alter(topo_obj, "b = residual_values.get(str(resi), 0.0)", space={'residual_values': residual_values})
        selection = f"{topo_obj} and resi {resi_list}"
        cmd.spectrum("b", color_palette, selection=selection, minimum=min_val, maximum=max_val)
    print(
        f"The minimum number of {topology_type} contacts in {molecule_name} for a single residue is {min_val}. It is colored with {colors[0]}.")
    print(
        f"The maximum number of {topology_type} contacts in {molecule_name} for a single residue is {max_val}. It is colored with {colors[1]}.")