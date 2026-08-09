"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

Function that creates a topological relations matrix plot for a whole model
"""
import matplotlib.pyplot as plt
import numpy as np

from functions.plots._palette import MODEL_COLORS, MODEL_LABELS, discrete_cmap


def matrix_plot_model(mat: np.ndarray, protid: str) -> None:
    """
    Plots the topological relationship matrix for a whole model (multiple chains).

    Args:
        mat (numpy.ndarray): The topological relationship matrix.
        protid (str): Protein identifier.
    """
    cmap, norm = discrete_cmap(MODEL_COLORS)

    fig, ax = plt.subplots()

    pngmat = ax.matshow(mat, cmap=cmap, norm=norm)
    ax.set_title(protid)
    ax.tick_params(
        labelleft=False,
        labelbottom=False,
        bottom=False,
        left=False,
        top=False,
        labeltop=False,
    )

    ticks = np.arange(len(MODEL_COLORS)) + 0.5
    cbar = fig.colorbar(pngmat, ax=ax, ticks=ticks, spacing="uniform")
    cbar.ax.set_yticklabels(MODEL_LABELS)
    cbar.ax.tick_params(length=0)
    cbar.set_label("Topological relation")
