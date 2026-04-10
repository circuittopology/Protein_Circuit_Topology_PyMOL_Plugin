"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

For exporting amount of PSC contacts to a csv file.
also checks whether data came from model or single chain contact map
"""
import logging
from collections.abc import Sequence
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
_psc_len = 4

def export_psc(psclist: Sequence[Sequence[object]], output_dir: Path) -> None:
    """
    Exports the counts of Parallel, Series, and Cross contacts (and others) to a CSV file.

    Args:
        psclist (list): A list of PSC statistics.
        output_dir (Path): The directory to save the CSV file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    if isinstance(psclist[0], str):
        if len(psclist) == _psc_len:
            df = pd.DataFrame(psclist,columns=["protid","P","S","C"])
        else:
            df = pd.DataFrame(psclist,columns=["protid","P","S","C","I","T","L"])
    elif len(psclist[0]) == _psc_len:
        df = pd.DataFrame(psclist,columns=["protid","P","S","C"])
    else:
        df = pd.DataFrame(psclist,columns=["protid","P","S","C","I","T","L"])

    output_path = output_dir / "pscresults.csv"
    df.to_csv(output_path)
    logger.info("Succesfully exported pscresults.csv to %s", output_path)
