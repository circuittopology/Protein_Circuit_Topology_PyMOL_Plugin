"""Colour scheme for the topological relation matrix plots."""
from matplotlib.colors import BoundaryNorm, ListedColormap

SINGLE_CHAIN_COLORS = (
    "#f0efec",  # 0
    "#4a3aa7",  # 1  S      series
    "#2a78d6",  # 2  P      parallel
    "#86b6ef",  # 3  P-1    inverse parallel
    "#0b0b0b",  # 4  X      cross
    "#eb6834",  # 5  CP     concurrent parallel
    "#f59a6b",  # 6  CP-1   concurrent inverse parallel
    "#9085e9",  # 7  CS     concurrent series
)
SINGLE_CHAIN_LABELS = ("-", "S", "P", "P-1", "X", "CP", "CP-1", "CS")

MODEL_COLORS = (
    "#f0efec",  # 0
    "#2a78d6",  # 1  P   parallel
    "#4a3aa7",  # 2  S   series
    "#0b0b0b",  # 3  X   cross
    "#eb6834",  # 4  I   independent
    "#f59a6b",  # 5  T   tandem
    "#86b6ef",  # 6  L   loop
)
MODEL_LABELS = ("-", "P", "S", "X", "I", "T", "L")

CONTACT_COLORS = {
    "P": SINGLE_CHAIN_COLORS[2],
    "S": SINGLE_CHAIN_COLORS[1],
    "X": SINGLE_CHAIN_COLORS[4],
}

PYMOL_CONTACT_COLORS = {"P": "ctp", "S": "cts", "X": "ctx"}


def discrete_cmap(colors):
    """Return (cmap, norm) mapping integer code i to colors[i], for any subset of codes."""
    n = len(colors)
    return ListedColormap(colors), BoundaryNorm(range(n + 1), n)
