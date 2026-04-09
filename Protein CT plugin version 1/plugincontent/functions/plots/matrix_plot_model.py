"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

Function that creates a topological relations matrix plot for a whole model
"""
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
import warnings
from typing import Any

def matrix_plot_model(mat: np.ndarray, protid: str) -> Any:
    """
    Creates a topological relations matrix plot for a whole model.
    
    Args:
        mat: The topological relations matrix to plot.
        protid: The protein ID.
        
    Returns:
        The matplotlib figure.
    """
    newcolors = np.array([[218/255, 219/255, 228/255,1], #Grey (-)
                        [172/255,200/255,247/255,1],    #Blue (P)
                        [131/255, 139/255, 197/255,1],  #Purple (S)
                        [186/255, 155/255, 201/255,1],  #Pink (X)
                        [72/255,81/255,153/255,1],      # Dark Purple (I)   
                        [156/255,204/255,102/255,1],    #Green (T)
                        [255/255,199/255,89/255,1]])     #Yellow (L)
                    
    newcmp = ListedColormap(newcolors)

    fig, ax = plt.subplots() 
    color = plt.get_cmap(newcmp, 7)

    pngmat = ax.matshow(mat,cmap=color,vmin = np.min(mat)-.5, vmax = np.max(mat)+.5)
    ax.set_title(protid)
    ax.tick_params(labelleft = False,labelbottom = False,bottom = False,left= False,top = False,labeltop = False)
    cbar = fig.colorbar(pngmat, ticks=np.arange(7))
    with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            cbar.ax.set_yticklabels(['-','P','S','X','I','T','L'])                   
    
    return fig
