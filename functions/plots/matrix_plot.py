"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

Function that creates a topological relations matrix plot for a single chain
"""
import matplotlib.pyplot as plt
import numpy as np

from functions.plots._display import show
from functions.plots._palette import (
    SINGLE_CHAIN_COLORS,
    SINGLE_CHAIN_LABELS,
    discrete_cmap,
)


def matrix_plot(mat: np.ndarray, protid: str) -> None:
    """
    Plots the topological relationship matrix for a single chain.

    Args:
        mat (numpy.ndarray): The topological relationship matrix.
        protid (str): Protein identifier.
    """
    cmap, norm = discrete_cmap(SINGLE_CHAIN_COLORS)

    fig, ax = plt.subplots()

    pngmat = ax.imshow(mat, cmap=cmap, norm=norm, interpolation="nearest")
    ax.set_xlabel("Intramolecular contact #")
    ax.set_ylabel("Intramolecular contact #")
    ax.set_title(protid)
    ax.tick_params(labelleft=True, labelbottom=True, bottom=False, left=False)

    ticks = np.arange(len(SINGLE_CHAIN_COLORS)) + 0.5
    cbar = fig.colorbar(pngmat, ax=ax, ticks=ticks, spacing="uniform")
    cbar.ax.set_yticklabels(SINGLE_CHAIN_LABELS)
    cbar.ax.tick_params(length=0)

    cbar.set_label("Topological relation")
    show(fig)
