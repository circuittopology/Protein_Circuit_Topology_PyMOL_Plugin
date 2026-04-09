"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

Function that plots the amount of psc and entangled contacts
"""
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Union, Any

def stats_plot(entangled: np.ndarray, psc: List[Union[str, int, float]], protid: str) -> Any:
    """
    Plots the amount of psc and entangled contacts.
    
    Args:
        entangled: Array containing the fraction of entangled contacts.
        psc: A list of PSC stats.
        protid: The protein ID.
        
    Returns:
        The matplotlib figure.
    """
    psc_vals = psc[1:]
    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.plot(entangled)
    ax2.pie(psc_vals, autopct=autopct_funct, pctdistance=1.25)
    ax1.set_xlabel('Distance from diagonal')
    ax1.set_ylabel('Fraction entangled')
    fig.suptitle(protid)
    base_labels = ['Parallel', 'Series', 'Cross']
    if len(psc_vals) > 3:
        extra_labels = ['I2', 'I3', 'I4', 'T2', 'T3', 'L']
        legend_labels = base_labels + extra_labels
    else:
        legend_labels = base_labels[:len(psc_vals)]
    ax2.legend(legend_labels, bbox_to_anchor=(.5, -0.5, 0.5, 0.5))
    plt.show()
    return fig

def autopct_funct(pct: float) -> str:
    """
    Format string for pie chart percentages.
    
    Args:
        pct: The percentage value.
        
    Returns:
        Formatted percentage string.
    """
    return f'{pct:.1f}%' if pct >= 1.0 else ''
