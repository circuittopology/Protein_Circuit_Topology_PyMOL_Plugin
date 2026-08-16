"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

Function that plots the amount of psx and entangled contacts
"""
from collections.abc import Sequence

import matplotlib.pyplot as plt
import numpy as np

from functions.plots._display import show

_contact_count = 3

def stats_plot(entangled: np.ndarray, psx: Sequence[float], protid: str) -> None:
    """
    Plots the fraction of entangled contacts versus distance from
    the diagonal and a pie chart of contact types.

    Args:
        entangled (numpy.ndarray): Array of entangled contact fractions.
        psx (Sequence[float]): List of contact type counts (P, S, X, etc.).
        protid (str): Protein identifier.
    """
    psx = psx[1:]
    fig,axes= plt.subplots(1,2)
    ax1, ax2 = axes
    ax1.plot(entangled)
    ax2.pie(psx,autopct = autopct_funct, pctdistance=1.25)
    ax1.set_xlabel("Distance from diagonal")
    ax1.set_ylabel("Fraction entangled")
    fig.suptitle(protid)
    base_labels = ["Parallel","Series","Cross"]
    if len(psx) > _contact_count:
        extra_labels = ["I2", "I3", "I4", "T2", "T3", "L"]
        legend_labels = base_labels + extra_labels
    else:
        legend_labels = base_labels[:len(psx)]
    ax2.legend(legend_labels, bbox_to_anchor=(.5, -0.5, 0.5, 0.5))
    show(fig)

def autopct_funct(pct: float) -> str:
    return f"{pct:.1f}%" if pct >= 1.0 else ""
