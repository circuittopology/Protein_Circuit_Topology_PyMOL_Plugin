from typing import Optional

import numpy as np
from pymol import cmd

def get_topology_vector(
    mat: np.ndarray,
    index: np.ndarray,
    topology_type: str,
    numbering: np.ndarray
) -> Optional[np.ndarray]:
    """
    Calculates a topology vector representing the density of a specific contact type
    for each residue.

    Args:
        mat (numpy.ndarray): The topological relationship matrix.
        index (numpy.ndarray): Array of contact indices.
        topology_type (str): The type of topology to calculate ('P', 'S', 'X').
        numbering (list or numpy.ndarray): List of residue numbers/identifiers.

    Returns:
        numpy.ndarray: The calculated topology vector.
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


def color_by_topology(
    molecule_name: str,
    topology_vector: np.ndarray,
    numbering: np.ndarray,
    topology_type: str
) -> None:
    """
    Colors a PyMOL object based on a topology vector.

    Args:
        molecule_name (str):
            The name of the PyMOL object to color.
        topology_vector (numpy.ndarray):
            The topology vector containing values for coloring.
        numbering (list or numpy.ndarray):
            List of residue numbers corresponding to the vector.
        topology_type (str): 
            The type of topology being visualized ('P', 'S', 'X'), used for color selection.
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
    resi_list = "+".join(map(str, numbering))
    min_val, max_val = float(np.min(topology_vector)), float(np.max(topology_vector))
    cmd.alter(topo_obj, "b = residual_values.get(str(resi), 0.0)", space={'residual_values': residual_values})
    selection = f"{topo_obj} and resi {resi_list}"
    cmd.spectrum("b", color_palette, selection=selection, minimum=min_val, maximum=max_val)
    print(
        f"The minimum number of {topology_type} contacts in {molecule_name} for a single residue is {min_val}. It is colored with {colors[0]}.")
    print(
        f"The maximum number of {topology_type} contacts in {molecule_name} for a single residue is {max_val}. It is colored with {colors[1]}.")
