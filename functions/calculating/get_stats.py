"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

Function for calculating the percentage of entangled contacts further along the diagonal
"""
import logging

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

_max_mat = 7
_diag = 2

def get_stats(mat: np.ndarray) -> np.ndarray:
    """
    Calculates the percentage of entangled contacts (Parallel and Cross) further along the diagonal.

    Args:
        mat (numpy.ndarray): The topological relationship matrix.

    Returns:
        numpy.ndarray: An array containing the percentage of entangled contacts for each diagonal.
    """
    if mat.shape == (0,0):
        logger.error("Error - mat empty")
        return np.array([0])
    #Calculates amount of overlapping(entangled), P and X, contacts across the diagonal
    entangled = np.zeros([len(mat),1])
    if mat.max() == _max_mat:
        for i in range(len(mat)-1):
            diag = np.diag(mat,k=i)
            entangled[i] = 1 - (sum(diag == 1)+ sum(diag == _max_mat))/len(diag)
    else:
        for i in range(len(mat)-1):
            diag = np.diag(mat,k=i)
            entangled[i] = 1 - (sum(diag == _diag)/len(diag))

    return entangled
