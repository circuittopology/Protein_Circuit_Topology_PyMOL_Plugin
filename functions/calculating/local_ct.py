from typing import Dict, Sequence, Union
import numpy as np

def local_ct(index: np.ndarray, mat: np.ndarray, numbering: Union[Sequence[int], np.ndarray]) -> Dict[int, Dict[str, int]]:
    """
    Calculates local circuit topology statistics for each residue.

    Args:
        index (numpy.ndarray): Array of contact indices.
        mat (numpy.ndarray): The topological relationship matrix.
        numbering (list or numpy.ndarray): List of residue numbers/identifiers.

    Returns:
        dict: A dictionary where keys are residue indices and values are dictionaries containing
              counts of 'P' (Parallel), 'IP' (Inverse Parallel), 'X' (Cross), and 'S' (Series) contacts.
    """
    localct = {}
    for i in range(len(numbering)):
        localct[i] = {"P":0,"IP":0,"X":0,"S":0}
    for i in range(len(numbering)):
        d = np.nonzero(index == i)
        localct[i]['IP'] = len(np.nonzero(np.sum((mat[d[0],:] == 5) | (mat[d[0],:] == 2),0))[0])
        localct[i]['P'] = len(np.nonzero(np.sum((mat[d[0],:] == 3) | (mat[d[0],:] == 6),0))[0])
        localct[i]['X'] = len(np.nonzero(np.sum(mat[d[0],:] == 4,0))[0])
        localct[i]['S'] = len(np.nonzero(np.sum((mat[d[0],:] == 7) | (mat[d[0],:] == 1),0))[0])

    return localct