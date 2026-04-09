"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

For exporting amount of PSC contacts to a csv file. 
also checks whether data came from model or single chain contact map
"""
import pandas as pd
import os
from typing import List, Union

def export_psc(psclist: List[Union[str, int, List[Union[str, int]]]], output_dir: str) -> None:
    """
    Exports amount of PSC contacts to a csv file.
    
    Args:
        psclist: A list containing PSC stats or lists of PSC stats.
        output_dir: The directory to save the output CSV.
    """
    os.makedirs(output_dir, exist_ok=True)
    if type(psclist[0]) == str:
        if len(psclist) == 4:
            df = pd.DataFrame(psclist, columns=['protid','P','S','C'])
        else:
            df = pd.DataFrame(psclist, columns=['protid','P','S','C','I','T','L'])
    elif len(psclist[0]) == 4:
        df = pd.DataFrame(psclist, columns=['protid','P','S','C'])
    else:
        df = pd.DataFrame(psclist, columns=['protid','P','S','C','I','T','L'])

    output_path = os.path.join(output_dir, "pscresults.csv")
    df.to_csv(output_path)
    print(f'Succesfully exported pscresults.csv to {output_dir}')
