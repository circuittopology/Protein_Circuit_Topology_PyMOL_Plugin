"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

Function that creates a residue contact map plot
"""
import matplotlib.pyplot as plt
import numpy as np

_indice_check_size = 2

def circuit_plot(index: np.ndarray, protid: str, numbering: np.ndarray) -> None:
    """
    Plots the circuit topology of a protein as a series of arcs.

    Args:
        index (numpy.ndarray): Array of contact indices.
        protid (str): Protein identifier.
        numbering (list or numpy.ndarray): List of residue numbers/identifiers.
    """
    plt.ion()

    if len(np.shape(numbering)) > 1:
        numbering = numbering[:,1]

    ax = plt.subplots()[1]
    plt.plot()
    plt.xlim(0,len(numbering)+1)
    plt.hlines(0,0,len(numbering)+1,colors = "k",linestyles="dashed")
    ax.tick_params(labelleft = False)
    ax.set_xlabel("Residue #")
    ax.set_title(protid)
    if len(index[0]) == _indice_check_size:

        for row in index:
            x = np.array([row[0],row[1]])
            r = (x[1]-x[0])/2
            center = np.mean(x)
            xx = np.arange(x[0],x[1]+0.001,0.01)
            np.seterr(invalid = "ignore")
            yy = np.sqrt(r**2 - (xx - center)**2)
            where_nans = np.isnan(yy)
            yy[where_nans] = 0
            plt.plot(xx,yy,
                    color ="k")

    else:
        chains = np.unique(np.array(index)[:,[2,3]])
        enum = np.array(range(len(chains)))
        colours = ["r","b","g"]

        for row in index:

            x = np.array([int(row[0]),int(row[1])])
            r = (x[1]-x[0])/2
            center = np.mean(x)
            xx = np.arange(x[0],x[1]+0.001,0.01)
            np.seterr(invalid = "ignore")
            yy = np.sqrt(r**2 - (xx - center)**2)
            where_nans = np.isnan(yy)
            yy[where_nans] = 0
            if row[2] != row[3]:
                color1 = "y"
                zorder = 1
            else:
                color1 = colours[enum[chains == row[2]][0]%3]
                zorder = 10

            plt.plot(xx,yy, color = color1, zorder = zorder)
