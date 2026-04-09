"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

For transforming Residue contact map indices to a contact map and exporting that to a csv file.
"""
import numpy as np 
import pandas as pd
import os 

def export_cmap3(index: np.ndarray, protid: str, numbering: np.ndarray, output_dir: str) -> None:
    """
    Transforms Residue contact map indices to a contact map and exports it to a csv file.
    
    Args:
        index: An array of contact indices.
        protid: The protein ID.
        numbering: The residue numbering array.
        output_dir: The directory to save the output CSV.
    """
    os.makedirs(output_dir, exist_ok=True)
    cmap = np.zeros([len(numbering), len(numbering)], dtype='int')
    
    for row in index:
        x = row[0]
        y = row[1]
        cmap[x][y] = 1
        cmap[y][x] = 1

    df = pd.DataFrame(cmap)
    fpath = os.path.abspath(os.path.join(output_dir, f"{protid}_cmap3.csv"))
    df.to_csv(fpath, header=False, index=False)
    print(f'Succesfully saved {protid}_cmap3.csv to {output_dir}.')
