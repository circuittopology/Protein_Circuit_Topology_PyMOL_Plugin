"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

For exporting amount of PSC contacts to a csv file. 
also checks whether data came from model or single chain contact map
"""
import os
import pandas as pd

def export_psc(
        psclist: list,
        output_dir: str
    ) -> None:
    """
    Function for exporting psc statistics to a csv located in output_dir

    Parameters
    psclist : list
        nested list of combined results containing protid,p,s,c
    output_dir : str
        directory where the csv file will be saved

    Returns
    None
    """
    os.makedirs(output_dir, exist_ok=True)
    if isinstance(psclist[0], str):
        if len(psclist) == 4:
            df = pd.DataFrame(psclist,columns=['protid','P','S','C'])
        else:
            df = pd.DataFrame(psclist,columns=['protid','P','S','C','I','T','L'])
    elif len(psclist[0]) == 4:
        df = pd.DataFrame(psclist,columns=['protid','P','S','C'])
    else:
        df = pd.DataFrame(psclist,columns=['protid','P','S','C','I','T','L'])

    output_path = os.path.join(output_dir, "pscresults.csv")
    df.to_csv(output_path)
    print(f'Succesfully exported pscresults.csv to {output_dir}')
