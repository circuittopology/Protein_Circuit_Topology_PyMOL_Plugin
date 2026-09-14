"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

Function for calculating the fraction of Parallel and Cross (non-Series) relations along each
diagonal of the relation matrix. ProteinCT calls this the "entangled" fraction.
"""
import logging

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

_max_mat = 7
_diag = 2

def get_stats(mat: np.ndarray) -> np.ndarray:
    """
    Calculates the fraction of Parallel and Cross (non-Series) relations on each diagonal of the
    relation matrix, i.e. as a function of the distance between two contact pairs in the contact list.
    This is the quantity ProteinCT calls the "entangled" fraction.

    Args:
        mat (numpy.ndarray): The topological relationship matrix.

    Returns:
        numpy.ndarray: One value per diagonal, the fraction of P + X relations on it.
    """
    if mat.shape == (0,0):
        logger.error("Error - mat empty")
        return np.array([0])
    # One minus the share of Series-type relations (Series and concerted series) on each diagonal
    px_fraction = np.zeros([len(mat),1])
    if mat.max() == _max_mat:
        for i in range(len(mat)-1):
            diag = np.diag(mat,k=i)
            px_fraction[i] = 1 - (sum(diag == 1)+ sum(diag == _max_mat))/len(diag)
    else:
        for i in range(len(mat)-1):
            diag = np.diag(mat,k=i)
            px_fraction[i] = 1 - (sum(diag == _diag)/len(diag))

    return px_fraction
