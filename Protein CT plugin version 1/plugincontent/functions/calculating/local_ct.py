import numpy as np
from typing import Dict

def local_ct(index: np.ndarray, mat: np.ndarray, numbering: np.ndarray) -> Dict[int, Dict[str, int]]:
    """
    Calculates the local circuit topology parameters.
    
    Args:
        index: An array of contact indices.
        mat: The topological relationship matrix.
        numbering: The residue numbering array.
        
    Returns:
        A dictionary containing local CT parameters for each residue index.
    """
    localct: Dict[int, Dict[str, int]] = {}
    for i in range(len(numbering)):
        localct[i] = {"P": 0, "IP": 0, "X": 0, "S": 0}
    for i in range(len(numbering)):
        d = np.nonzero(index == i)
        localct[i]['IP'] = len(np.nonzero(np.sum((mat[d[0], :] == 5) | (mat[d[0], :] == 2), 0))[0])
        localct[i]['P'] = len(np.nonzero(np.sum((mat[d[0], :] == 3) | (mat[d[0], :] == 6), 0))[0])
        localct[i]['X'] = len(np.nonzero(np.sum(mat[d[0], :] == 4, 0))[0])
        localct[i]['S'] = len(np.nonzero(np.sum((mat[d[0], :] == 7) | (mat[d[0], :] == 1), 0))[0])
    
    return localct
