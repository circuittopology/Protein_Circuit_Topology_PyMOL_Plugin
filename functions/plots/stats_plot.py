"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

Function that plots the relation-type counts and the fraction of P + X relations per diagonal
"""
from collections.abc import Sequence

import matplotlib.pyplot as plt
import numpy as np

from functions.plots._display import show

SINGLE_CHAIN_LABELS = ("Parallel", "Series", "Cross")
MULTI_CHAIN_LABELS = ("Parallel", "Series", "Cross", "I2", "I3", "I4", "T2", "T3", "L")

def stats_plot(px_fraction: np.ndarray, psx: Sequence[float], protid: str) -> None:
    """
    Plots the fraction of Parallel and Cross (non-Series) relations versus distance from
    the diagonal of the relation matrix, and a pie chart of the relation types.

    ProteinCT calls the left-hand quantity the "entangled" fraction; it is a statement about
    relation types, not about geometric entanglement.

    Args:
        px_fraction (numpy.ndarray): Fraction of P + X relations per diagonal, as returned by get_stats.
        psx (Sequence[float]): A statistics row as returned by get_matrix.
        protid (str): Protein identifier.
    """
    counts = list(psx[1:])
    if len(counts) == len(MULTI_CHAIN_LABELS):
        labels = MULTI_CHAIN_LABELS
    else:
        counts = counts[:len(SINGLE_CHAIN_LABELS)]
        labels = SINGLE_CHAIN_LABELS[:len(counts)]

    fig,axes= plt.subplots(1,2)
    ax1, ax2 = axes
    ax1.plot(px_fraction)
    ax2.pie(counts,autopct = autopct_funct, pctdistance=1.25)
    ax1.set_xlabel("Distance from diagonal")
    ax1.set_ylabel("Fraction of P + X relations")
    fig.suptitle(protid)
    ax2.legend(labels, bbox_to_anchor=(.5, -0.5, 0.5, 0.5))
    show(fig)

def autopct_funct(pct: float) -> str:
    return f"{pct:.1f}%" if pct >= 1.0 else ""
