"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

Function that plots the amount of psc and entangled contacts
"""
import matplotlib.pyplot as plt
import numpy as np

def stats_plot(
        entangled: np.ndarray,
        psc: list,
        protid: str
    ) -> None:
    """
    Function for plotting a of the fractions of different types of CT relations and
    entanglement across the cmap diagonal

    Parameters
    entangled : np.ndarray
        Percentage of entangled contacts (P & X) across the diagonal.
        Measure of globularity
    psc : list
        Amount of parallel, series, cross contacts in chain
    protid : str
        Protein ID

    Returns
    None
    """
    psc = psc[1:]
    fig,(ax1,ax2)= plt.subplots(1,2)
    ax1.plot(entangled)
    ax2.pie(psc,autopct = autopct_funct, pctdistance=1.25)
    ax1.set_xlabel('Distance from diagonal')
    ax1.set_ylabel('Fraction entangled')
    fig.suptitle(protid)
    base_labels = ['Parallel','Series','Cross']
    if len(psc) > 3:
        extra_labels = ['I2', 'I3', 'I4', 'T2', 'T3', 'L']
        legend_labels = base_labels + extra_labels
    else:
        legend_labels = base_labels[:len(psc)]
    ax2.legend(legend_labels, bbox_to_anchor=(.5, -0.5, 0.5, 0.5))
    plt.show()

def autopct_funct(pct):
    return f'{pct:.1f}%' if pct >= 1.0 else ''
