"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

Function for applying an energy filter on an existing Residue contact map

input   =   indices of contact map, array of residue ID's, list of residue names,
            4 letter protein id, energy filter type
output  =   indices of filtered contact map, protein ID
"""
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def energy_cmap(
    index: np.ndarray,
    numbering: np.ndarray,
    res_names: list[str],
    protid: str,
    potential_sign: str = "-",
) -> tuple[np.ndarray, str]:
    """
    Applies an energy filter to an existing residue contact map based on a potential matrix.

    Args:
        index (numpy.ndarray): Array of contact indices.
        numbering (list or numpy.ndarray): List of residue numbers/identifiers.
        res_names (list): List of residue names corresponding to the numbering.
        protid (str): Protein identifier.
        potential_sign (str, optional): The sign of the potential to filter by ('+' or '-'). Defaults to '-'.

    Returns:
        tuple: A tuple containing the filtered contact indices (numpy.ndarray) and the updated protein identifier (str).
    """
    #Checking if contacts are present
    if index.shape == (0,):
        logger.info("Energy filtering failed - Empty index")
        return index,protid

    #amino acid keys
    n_amino = 20
    aamap = np.array(["CYS","MET","PHE","ILE","LEU","VAL","TRP","TYR","ALA","GLY","THR","SER","GLN","ASN","GLU","ASP","HIS","ARG","LYS","PRO"])

    y = index[:,0]
    x = index[:,1]

    numbering = np.array([numbering]).T

    np_res_names: NDArray[np.str_]  = np.array(res_names)

    resnames1 = np_res_names[y]
    resnames2 = np_res_names[x]

    #transform txt file of potential matrix into array
    plugin_dir = Path(__file__).parent
    txt_path = plugin_dir / "matrix_potential.txt"
    potential_matrix = np.loadtxt(txt_path,"object")
    nan_matrix = potential_matrix == "n"
    nan_matrix = nan_matrix * 1
    potential_matrix[potential_matrix == "n"] = 100
    potential_matrix = potential_matrix.astype("float")


    for i in range(n_amino):
        for j in range(n_amino):
            if potential_matrix[i][j] == 0:
                potential_matrix[i][j] = 10
                potential_matrix[j][i] = 10
            if nan_matrix[i][j] == 1:
                potential_matrix[i][j]=potential_matrix[j][i]

    #linking resnames to res keys and finding score in potential_matrix
    energy_cmap = np.zeros([len(numbering),len(numbering)],"float")

    for i in range(len(x)):
        score = potential_matrix[aamap == resnames1[i],aamap == resnames2[i]][0]
        energy_cmap[x[i]][y[i]] = score
        energy_cmap[y[i]][x[i]] = score

    #determine type of filtering
    if potential_sign == "+":
        energy_cmap = (energy_cmap > 0) * 1
    elif potential_sign == "-":
        energy_cmap = (energy_cmap < 0) * 1
    else:
        raise TypeError

    #transform into indices
    energy_cmap = np.transpose(np.nonzero(np.triu(energy_cmap)))
    protid = f"{protid}_{potential_sign}_ef"

    return energy_cmap,protid
