"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

Function for calculating the percentage of entangled contacts further along the diagonal
"""
import numpy as np  

def get_stats(mat: np.ndarray) -> np.ndarray:
    """
    Calculates the percentage of entangled contacts further along the diagonal.
    
    Args:
        mat: The topological relationship matrix.
        
    Returns:
        An array containing the calculated percentages of entangled contacts across the diagonal.
    """
    if mat.shape == (0,0) or mat.size == 0:
        print('Error - mat empty')
        return np.array([0])
    #Calculates amount of overlapping(entangled), P and X, contacts across the diagonal
    entangled = np.zeros([len(mat), 1])
    if mat.max() == 7:
        for i in range(0, len(mat)-1):
            diag = np.diag(mat, k=i)
            if len(diag) > 0:
                entangled[i] = 1 - (sum(diag == 1) + sum(diag == 7)) / len(diag)
    else:
        for i in range(0, len(mat)-1):
            diag = np.diag(mat, k=i)
            if len(diag) > 0:
                entangled[i] = 1 - (sum(diag == 2) / len(diag))

    return entangled
