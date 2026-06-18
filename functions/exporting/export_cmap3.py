"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

For transforming Residue contact map indices to a contact map and exporting that to a csv file.
"""
import logging
from pathlib import Path

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def export_cmap3(index: np.ndarray, protid: str, numbering: np.ndarray, output_dir: Path) -> None:
    """
    Exports a residue contact map (as a binary matrix) to a CSV file.

    Args:
        index (numpy.ndarray): Array of contact indices.
        protid (str): Protein identifier.
        numbering (Sequence[int]): List of residue numbers/identifiers.
        output_dir (str): The directory to save the CSV file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    cmap = np.zeros([len(numbering),len(numbering)],dtype="int")

    for row in index:
        x = row[0]
        y = row[1]
        cmap[x][y] = 1
        cmap[y][x] = 1

    df = pd.DataFrame(cmap)
    fpath = output_dir / f"{protid}_cmap3.csv"
    df.to_csv(fpath, header = False,index = False)
    logger.info("Successfully saved %s_cmap3.csv to %s.", protid, output_dir)
