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


def register_shades() -> None:
    """Define every shade colour, blended from white towards each contact-type hue (once per session)."""
    for topology_type, hue in VIEWER_CONTACT_COLORS.items():
        rgb = np.asarray(to_rgb(hue))
        for level in range(BUCKETS):
            fraction = MIN_SHADE + (1.0 - MIN_SHADE) * (level / max(BUCKETS - 1, 1))
            cmd.set_color(f"{PYMOL_CONTACT_COLORS[topology_type]}{level}", (1.0 - fraction * (1.0 - rgb)).tolist())


def _shade_levels(n_bounds: int) -> list[int]:
    """Pick `n_bounds` shades spread across the registered range, so the top is always full."""
    if n_bounds <= 1:
        return [BUCKETS - 1]
    return [round(i * (BUCKETS - 1) / (n_bounds - 1)) for i in range(n_bounds)]


def _shade_fraction(level: int, of: int) -> float:
    """How far towards the hue a given level sits. Level 0 is white; the rest start at MIN_SHADE."""
    if level <= 0:
        return 0.0
    return MIN_SHADE + (1.0 - MIN_SHADE) * ((level - 1) / max(of - 1, 1))


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

    scope = f"{molecule_name} and polymer"

    if not bounds:
        cmd.color("white", scope)
        logger.info("No %s relations anywhere in %s; left white.", topology_type, molecule_name)
        return bounds

    hue = PYMOL_CONTACT_COLORS[topology_type]
    cmd.set_color(hue, to_rgb(VIEWER_CONTACT_COLORS[topology_type]))

    values = np.asarray(topology_vector, dtype=float)
    level = np.searchsorted(np.asarray(bounds, dtype=float), values, side="left") + 1
    level = np.where(values > 0, np.minimum(level, len(bounds)), 0)
    shade = [_shade_fraction(int(lv), len(bounds)) for lv in level]
    per_residue = {
        str(res): (float(count), float(frac))
        for res, count, frac in zip(numbering, values, shade, strict=True)
    }
    cmd.alter(scope, "b, q = per_residue.get(str(resi), (0.0, 0.0))",
              space={"per_residue": per_residue})
    cmd.spectrum("q", f"white_{hue}", selection=scope, minimum=0.0, maximum=1.0)

    logger.info(
        "Coloured %s by %s topology in %d levels, bounds %s.",
        molecule_name, topology_type, len(bounds), [int(b) for b in bounds],
    )

    return bounds


def make_scale_bar(topo_obj: str, topology_type: str, bounds: list[float]) -> str | None:
    """
    Put a stepped, labelled colour bar in the viewer so the numbers behind the colours show.

    Stepped because the colouring is, so what the legend shows is what the structure got.
    """
    if not bounds:
        return None

    register_shades()
    ramp_name = f"{topo_obj}_scale"
    stops: list[float] = [0.0]
    colours: list[str] = ["white"]
    low = 0.0

    for level, high in zip(_shade_levels(len(bounds)), bounds, strict=True):
        name = f"{PYMOL_CONTACT_COLORS[topology_type]}{level}"
        stops += [low + 1e-3, float(high)]
        colours += [name, name]
        low = float(high)

    try:
        cmd.ramp_new(ramp_name, topo_obj, stops, colours)
    except Exception:
        logger.debug("Could not create the scale bar %s", ramp_name, exc_info=True)
        return None

    return ramp_name
