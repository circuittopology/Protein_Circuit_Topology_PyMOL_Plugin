"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

Function applying a length filter to an existing residue contact map index
"""
import numpy as np

def length_filter(
        index: np.ndarray,
        distance: np.ndarray,
        mode: str = '<'
    ) -> np.ndarray:
    """
    Function that filters out either long range contacts or long range contacts out
    of cmap

    Parameters
    index: np.ndarray
        Residue contact map
    distance: np.ndarray
        threshold for length filtering in the number of residues between contacts.
    mode: str
        Setting for only including short range contacts (‘<’) and excluding long
        range contacts or including long range contacts (‘>’) and excluding
        short range contacts
    
    Returns
    entangled: np.ndarray
        Percentage of entangled contacts (P & X) across the diagonal.
        Measure of globularity
    """
    if index.shape == (0,):
        print('Error - index empty')
        return index
    #checks the indices if they meet the requirement for the lenght filtering
    new_index = []
    if mode == '<':
        for i in index:
            dis = abs(i[0]-i[1])
            if dis <= distance:
                new_index.append(list(i))
    if mode == '>':
        for i in index:
            dis = abs(i[0]-i[1])
            if dis >= distance:
                new_index.append(list(i))
    return np.array(new_index)
