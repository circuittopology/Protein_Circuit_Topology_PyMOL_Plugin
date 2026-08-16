"""Say when a Local Circuit Topology plot will come out blank."""
import numpy as np

from utils.helpers import notify

RELATION_CODES = {"S": (1, 7), "P": (3, 6), "IP": (5, 2), "X": (4,)}


def report_empty_local_result(idx, mat, residue_id, residue_number, contact) -> str:
    """
    Print a notice when the plot will highlight nothing; return "" when it will.

    `residue_id` is a POSITION into `numbering`; `residue_number` is what the user typed.
    """
    rows = np.where(idx == residue_id)[0]
    if rows.size and np.isin(mat[rows, :], RELATION_CODES.get(contact, ())).any():
        return ""
    return notify(
        f"Circuit Topology: residue {residue_number} takes part in {rows.size} contact(s) and has no "
        f"{contact} relations, so the local topology plot will not highlight anything. Try a "
        f"different contact type, or a larger cut-off distance.",
    )
