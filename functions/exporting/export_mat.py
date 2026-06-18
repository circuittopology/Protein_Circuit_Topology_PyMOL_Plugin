"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

For exporting a topological relations matrix to a csv.
"""
import logging
from pathlib import Path

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

_mat_small = 2
_mat_large = 4
def export_mat(index: np.ndarray, mat: np.ndarray, protid: str, output_dir: Path) -> None:
    """
    Exports the topological relationship matrix to a CSV file.

    Args:
        index (numpy.ndarray): Array of contact indices.
        mat (numpy.ndarray): The topological relationship matrix.
        protid (str): Protein identifier.
        output_dir (Path): The directory to save the CSV file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    if mat.shape == (0,0):
        logger.error("Error - mat is empty. Failed to export %s", protid)
        return

    if np.shape(index)[1] == _mat_small:

        d = {0:"-",1:"S",2:"P",3:"P-1",4:"C",5:"CP",6:"CP-1",7:"CS"}
        c = np.vectorize(d.get)(mat.astype(int))

        names = [f"[{index[i,0]} - {index[i,1]}]" for i in range(len(index))]

        df = pd.DataFrame(c,columns=names,index=names)
        fpath = output_dir / f"{protid}_mat.csv"
        df.to_csv(fpath,sep=";")
        logger.info("Succesfully saved %s", fpath)

    elif np.shape(index)[1] == _mat_large:

        d = {0:"-",1:"P",2:"S",3:"C",4:"I",5:"T",6:"L"}
        c = np.vectorize(d.get)(mat.astype(int))

        names = [f"[{index[i,0]}({index[i,2]}) - {index[i,1]}({index[i,3]})]" for i in range(len(index))]

        df = pd.DataFrame(c,columns=names,index=names)
        fpath = output_dir / f"{protid}_mat.csv"
        df.to_csv(fpath,sep=";")
        logger.info("Succesfully saved %s", fpath)
