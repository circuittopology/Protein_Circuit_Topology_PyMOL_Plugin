"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

For exporting a topological relations matrix to a csv. 
"""
import os
import numpy as np
import pandas as pd

def export_mat(index: np.ndarray, mat: np.ndarray, protid: str, output_dir: str) -> None:
    """
    Exports the topological relationship matrix to a CSV file.

    Args:
        index (numpy.ndarray): Array of contact indices.
        mat (numpy.ndarray): The topological relationship matrix.
        protid (str): Protein identifier.
        output_dir (str): The directory to save the CSV file.
    """
    os.makedirs(output_dir, exist_ok=True)
    if mat.shape == (0,0):
        print(f'Error - mat is empty. Failed to export {protid}')

    if np.shape(index)[1] == 2:

        d = dict({0:'-',1:'S',2:'P',3:'P-1',4:'C',5:'CP',6:'CP-1',7:'CS'})
        c = np.vectorize(d.get)(mat.astype(int))

        names = []
        for i in range(len(index)):
            names.append(f'[{index[i,0]} - {index[i,1]}]')
 
        df = pd.DataFrame(c,columns=names,index=names)
        fpath = os.path.join(output_dir, f"{protid}_mat.csv")
        df.to_csv(fpath,sep=';')
        print(f'Succesfully saved {protid}_mat.csv')

    elif np.shape(index)[1] == 4:

        d = dict({0:'-',1:'P',2:'S',3:'C',4:'I',5:'T',6:'L'})
        c = np.vectorize(d.get)(mat.astype(int))

        names = []
        for i in range(len(index)):
            names.append(f'[{index[i,0]}({index[i,2]}) - {index[i,1]}({index[i,3]})]')
 
        df = pd.DataFrame(c,columns=names,index=names)
        fpath = os.path.join(output_dir, f"{protid}_mat.csv")
        df.to_csv(fpath,sep=';')
        print(f'Succesfully saved {protid}_mat.csv')