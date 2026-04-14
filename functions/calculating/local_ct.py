from collections.abc import Sequence

import numpy as np

_ip = 5
_ip_minus = 2
_p = 3
_p_minus = 6
_x = 4
_s = 7

def local_ct(index: np.ndarray, mat: np.ndarray, numbering: Sequence[int] | np.ndarray) -> dict[int, dict[str, int]]:
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
        localct[i]["IP"] = len(np.nonzero(np.sum((mat[d[0],:] == _ip) | (mat[d[0],:] == _ip_minus),0))[0])
        localct[i]["P"] = len(np.nonzero(np.sum((mat[d[0],:] == _p) | (mat[d[0],:] == _p_minus),0))[0])
        localct[i]["X"] = len(np.nonzero(np.sum(mat[d[0],:] == _x,0))[0])
        localct[i]["S"] = len(np.nonzero(np.sum((mat[d[0],:] == _s) | (mat[d[0],:] == 1),0))[0])

    return localct
