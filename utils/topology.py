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

# Colour levels for the 3D maps.
BUCKETS = 5

# How far the faintest non-zero shade sits from white towards the contact-type hue.
MIN_SHADE = 0.35

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

def bucket_bounds(topology_vector: np.ndarray, n_buckets: int = BUCKETS) -> list[float]:
    """
    Upper bounds of the colour buckets, taken from the quantiles of the non-zero values.
    Zero is excluded because it gets its own white level and never shares a bucket.

    Args:
        topology_vector (numpy.ndarray): Per-residue values, as returned by
            ``get_topology_vector``.
        n_buckets (int): Requested number of non-zero levels. Fewer are returned when the
            values are too few or too repetitive to separate.

    Returns:
        list[float]: Strictly increasing bucket upper bounds; empty if nothing is non-zero.
    """
    nonzero = np.asarray(topology_vector)[np.asarray(topology_vector) > 0]
    if nonzero.size == 0:
        return []

    quantiles = np.linspace(100.0 / n_buckets, 100.0, n_buckets)
    bounds = (float(np.ceil(np.percentile(nonzero, q))) for q in quantiles)

    return sorted(set(bounds))


def _shade(topology_type: str, level: int, of: int) -> str:
    """Register and name the colour for one bucket, blended from white towards the hue."""
    base = PYMOL_CONTACT_COLORS[topology_type]
    fraction = MIN_SHADE + (1.0 - MIN_SHADE) * (level / max(of - 1, 1))
    rgb = np.asarray(to_rgb(VIEWER_CONTACT_COLORS[topology_type]))
    name = f"{base}_{level}"
    cmd.set_color(name, (1.0 - fraction * (1.0 - rgb)).tolist())

    return name


def color_by_topology(
    molecule_name: str,
    topology_vector: np.ndarray,
    numbering: np.ndarray,
    topology_type: str,
    bounds: list[float] | None = None,
) -> list[float] | None:
    """
    Colour a PyMOL object by a topology vector, in discrete levels.

    Args:
        molecule_name (str): The object OR selection to colour; its polymer atoms are used.
        topology_vector (numpy.ndarray): One value per residue, aligned to `numbering`.
        numbering (numpy.ndarray): Residue numbers.
        topology_type (str): 'P', 'S' or 'X'.
        bounds (list[float] | None): Bucket bounds to use. Pass the same list for every
            chain or trajectory frame that should share one scale; omit to derive them
            from this vector alone.

    Returns:
        The bucket bounds actually used, or None if the contact type was invalid.
    """
    if topology_type not in PYMOL_CONTACT_COLORS:
        logger.error("Please select a valid contact type!")
        return None

    if bounds is None:
        bounds = bucket_bounds(topology_vector)

    residual_values = {str(res): float(val) for res, val in zip(numbering, topology_vector, strict=True)}
    scope = f"({molecule_name}) and polymer"
    cmd.alter(scope, "b = residual_values.get(str(resi), 0.0)", space={"residual_values": residual_values})

    cmd.color("white", scope)

    low = 0.0
    for level, high in enumerate(bounds):
        name = _shade(topology_type, level, len(bounds))
        limit = "" if level == len(bounds) - 1 else f" and b < {high + 0.5}"
        cmd.color(name, f"({scope}) and b > {low}{limit}")
        low = high

    if bounds:
        logger.info(
            "Coloured %s by %s topology in %d levels, bounds %s (0 stays white, top is %s).",
            molecule_name, topology_type, len(bounds),
            [int(b) for b in bounds], VIEWER_CONTACT_COLORS[topology_type],
        )
    else:
        logger.info("No %s relations anywhere in %s; left white.", topology_type, molecule_name)

    return bounds


def make_scale_bar(topo_obj: str, topology_type: str, bounds: list[float]) -> str | None:
    """Put a stepped, labelled colour bar in the viewer so the numbers behind the colours show."""
    if not bounds:
        return None

    ramp_name = f"{topo_obj}_{topology_type}_scale"
    stops: list[float] = [0.0]
    colours: list[str] = ["white"]
    low = 0.0
    for level, high in enumerate(bounds):
        name = f"{PYMOL_CONTACT_COLORS[topology_type]}_{level}"
        stops += [low + 1e-3, float(high)]
        colours += [name, name]
        low = float(high)

    try:
        cmd.delete(ramp_name)
        cmd.ramp_new(ramp_name, topo_obj, stops, colours)
    except Exception:
        logger.debug("Could not create the scale bar %s", ramp_name, exc_info=True)
        return None

    return ramp_name
