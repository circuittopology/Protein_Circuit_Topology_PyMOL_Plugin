import logging

import numpy as np
from matplotlib.colors import to_rgb
from pymol import cmd

from functions.plots._palette import PYMOL_CONTACT_COLORS, VIEWER_CONTACT_COLORS

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

_parallel_contact_num_1 = 2
_parallel_contact_num_2 = 3
_cross_contact_num = 4

def get_topology_vector(
    mat: np.ndarray,
    index: np.ndarray,
    topology_type: str,
    numbering: np.ndarray,
) -> np.ndarray | None:
    """
    Per-residue participation in one class of contact-contact relation.

    Args:
        mat (numpy.ndarray): The topological relationship matrix.
        index (numpy.ndarray): Array of contact indices.
        topology_type (str): The type of topology to calculate ('P', 'S', 'X').
        numbering (numpy.ndarray): Residue numbers, one per residue present in the chain.

    Returns:
        numpy.ndarray: one value per residue, aligned element-for-element with `numbering`.
    """
    if topology_type == "S":
        vec = np.sum((mat == 1), axis=1)
    elif topology_type == "P":
        vec = np.sum(np.logical_or(mat == _parallel_contact_num_1, mat == _parallel_contact_num_2), axis=1)
    elif topology_type == "X":
        vec = np.sum((mat == _cross_contact_num), axis=1)
    else:
        logger.error("Please select a valid contact type!")
        return None

    per_residue = np.zeros(len(numbering), dtype=float)
    np.add.at(per_residue, index[:, 0], vec)
    np.add.at(per_residue, index[:, 1], vec)

    self_pairs = index[:, 0] == index[:, 1]
    if self_pairs.any():
        np.subtract.at(per_residue, index[self_pairs, 0], vec[self_pairs])

    return per_residue

def color_by_topology(
    molecule_name: str,
    topology_vector: np.ndarray,
    numbering: np.ndarray,
    topology_type: str,
    value_range: tuple[float, float] | None = None,
) -> tuple[float, float] | None:
    """
    Colour a PyMOL object by a topology vector

    Args:
        molecule_name (str): The PyMOL object to colour.
        topology_vector (numpy.ndarray): One value per residue, aligned to `numbering`.
        numbering (numpy.ndarray): Residue numbers.
        topology_type (str): 'P', 'S' or 'X'.
        value_range (tuple[float, float] | None): Force an explicit (low, high) scale.

    Returns:
        The (low, high) range actually used, or None if the contact type was invalid.
    """
    color_name = PYMOL_CONTACT_COLORS.get(topology_type)
    if color_name is None:
        logger.error("Please select a valid contact type!")
        return None

    cmd.set_color(color_name, to_rgb(VIEWER_CONTACT_COLORS[topology_type]))
    color_palette = f"white_{color_name}"
    topo_obj = molecule_name
    residual_values = {str(res): float(val) for res, val in zip(numbering, topology_vector, strict=True)}

    resi_list = "+".join(map(str, numbering))
    if value_range is None:
        min_val, max_val = float(np.min(topology_vector)), float(np.max(topology_vector))
    else:
        min_val, max_val = float(value_range[0]), float(value_range[1])

    cmd.alter(topo_obj, "b = residual_values.get(str(resi), 0.0)", space={"residual_values": residual_values})
    selection = f"{topo_obj} and resi {resi_list}"
    cmd.spectrum("b", color_palette, selection=selection, minimum=min_val, maximum=max_val)

    _make_scale_bar(topo_obj, topology_type, color_name, min_val, max_val)
    logger.info(
        "Coloured %s by %s topology over the range %.3f (white) to %.3f (%s).",
        molecule_name, topology_type, min_val, max_val, VIEWER_CONTACT_COLORS[topology_type],
    )

    return (min_val, max_val)


def _make_scale_bar(
    topo_obj: str, topology_type: str, color_name: str, min_val: float, max_val: float,
) -> str | None:
    """Put a labelled colour bar in the viewer so the numbers behind the colours are visible."""
    ramp_name = f"{topo_obj}_{topology_type}_scale"

    try:
        cmd.delete(ramp_name)
        mid = (min_val + max_val) / 2.0
        cmd.ramp_new(ramp_name, topo_obj, [min_val, mid, max_val], ["white", "white", color_name])
    except Exception:
        logger.debug("Could not create the scale bar %s", ramp_name, exc_info=True)
        return None

    return ramp_name
