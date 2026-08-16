"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

For exporting amount of PSX contacts to a csv file.
also checks whether data came from model or single chain contact map
"""
import logging
from collections.abc import Sequence
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
_psx_len = 4
_psx_wide = 7
PSX_FILENAME = "psxresults.csv"

def export_psx(psxlist: Sequence[Sequence[object]], output_dir: Path) -> None:
    """
    Exports the counts of Parallel (P), Series (S), and Cross (X) contacts (and others) to a CSV file.

    A batch run accumulates every input's row into one psxlist and calls this once, so a single
    output file is correct - there is nothing to disambiguate with a per-input name.

    Args:
        psxlist (list): A list of PSX statistic rows, or a single flat row.
        output_dir (Path): The directory to save the CSV file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = [list(psxlist)] if psxlist and isinstance(psxlist[0], str) else [list(r) for r in psxlist]
    if not rows:
        logger.warning("No PSX rows to export; %s was not written.", PSX_FILENAME)
        return

    widths = {len(r) for r in rows}
    if len(widths) != 1:
        msg = f"All PSX rows must have the same width, got {sorted(widths)}"
        raise ValueError(msg)
    width = widths.pop()
    if width == _psx_len:
        columns = ["protid", "P", "S", "X"]
    elif width == _psx_wide and any(isinstance(v, dict) for v in rows[0][_psx_len:]):
        columns = ["protid", "P", "S", "X", "I", "T", "L"]
    elif width == _psx_wide:
        columns = ["protid", "P", "S", "X", "P_frac", "S_frac", "X_frac"]
    else:
        msg = f"Unrecognised PSX row width: {width}"
        raise ValueError(msg)

    df = pd.DataFrame(rows, columns=columns)
    output_path = output_dir / PSX_FILENAME
    df.to_csv(output_path, index=False)
    logger.info("Successfully exported %s to %s", PSX_FILENAME, output_path)
