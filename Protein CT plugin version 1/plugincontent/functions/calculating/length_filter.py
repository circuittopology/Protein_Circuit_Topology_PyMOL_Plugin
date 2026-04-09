"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

Function applying a length filter to an existing residue contact map index
"""
import numpy as np

def length_filter(index: np.ndarray, distance: int, mode: str = '<') -> np.ndarray:
    """
    Applies a length filter to an existing residue contact map index.
    
    Args:
        index: An array of contact indices.
        distance: The distance to filter by.
        mode: The filtering mode ('<' for less than or equal to, '>' for greater than or equal to).
        
    Returns:
        The filtered array of contact indices.
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