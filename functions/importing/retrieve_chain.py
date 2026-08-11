"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

Function for creating the chain object used in Bio.PDB and all the functions. Can specify which chain

"""
import logging
import warnings
from itertools import pairwise
from pathlib import Path

from Bio import BiopythonWarning
from Bio.PDB.Chain import Chain
from Bio.PDB.MMCIFParser import MMCIFParser
from Bio.PDB.PDBParser import PDBParser

logger = logging.getLogger(__name__)

_MAX_REPORTED = 5


def retrieve_chain(input_file: Path, chainid: int | str = 0) -> tuple[Chain, str]:  # noqa: PLR0912
    """
    Retrieves a specific chain from a PDB or MMCIF file.

    Args:
        input_file (Path): Path to the input PDB or MMCIF file.
        chainid (int or str, optional): The chain ID to retrieve. Can be an integer index or a string ID. Defaults to 0.

    Returns:
        tuple: A tuple containing the chain object (Bio.PDB.Chain.Chain) and the protein ID (str).
    """
    input_path = Path(input_file)
    input_file_str = str(input_path)
    structure_id = input_path.stem
    if input_path.suffix.lower() == ".cif":
        # Suppress harmless warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", BiopythonWarning)
            # Import the protein data
            structure = MMCIFParser().get_structure(structure_id, input_file_str)
    else:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", BiopythonWarning)

            # import protein data
            structure = PDBParser(PERMISSIVE=True).get_structure(structure_id, input_file_str)

    if structure:
        model = structure[0]
    else:
        msg = f"No structure found in the input file: {input_file_str}"
        raise ValueError(msg)
    # removes heteroresidues from protein
    residue_to_remove = []
    chain_to_remove = []
    for chain in model:
        for residue in chain:
            if residue.id[0] != " ":
                residue_to_remove.append((chain.id, residue.id))
                continue
                # REMOVES DNA MOLECULES AND UNKNOWN RESIDUES FROM MODEL
            if residue.get_resname() in ["DG", "DA", "DT", "DC", "DU", "UNK", "A", "G", "C", "T"]:
                residue_to_remove.append((chain.id, residue.id))

    for residue in residue_to_remove:
        model[residue[0]].detach_child(residue[1])

    chain_to_remove = [chain.id for chain in model if len(chain.get_list()) == 0]

    for chain in chain_to_remove:
        model.detach_child(chain)

    if isinstance(chainid, int):
        chain = model.get_list()[chainid]
    elif isinstance(chainid, str):
        chain = model[chainid]
    else:
        msg_0 = f"Invalid type for chainid: {type(chainid)}. Must be int or str."
        raise TypeError(msg_0)

    protid = structure.id + "_" + chain.id
    warn_about_numbering(chain, protid)

    return chain, protid


def warn_about_numbering(chain: Chain, protid: str) -> list[str]:
    """Report the two residue-numbering situations that contact detection handles imprecisely."""
    residues = [res for res in chain if res.id[0] == " "]
    messages = []

    seen: dict[int, int] = {}
    for res in residues:
        seen[res.id[1]] = seen.get(res.id[1], 0) + 1
    duplicated = sorted(num for num, count in seen.items() if count > 1)
    if duplicated:
        shown = ", ".join(str(n) for n in duplicated[:_MAX_REPORTED])
        if len(duplicated) > _MAX_REPORTED:
            shown += f", and {len(duplicated) - _MAX_REPORTED} more"
        messages.append(
            f"{protid}: {len(duplicated)} residue number(s) occur more than once, i.e. insertion "
            f"codes are in use ({shown}). Contact detection matches on the residue number alone, so "
            f"atoms of the inserted residues are attributed to the first residue with that number.",
        )

    numbers = [res.id[1] for res in residues]
    breaks = [(a, b) for a, b in pairwise(numbers) if b - a > 1]
    if breaks:
        shown = ", ".join(f"{a}->{b}" for a, b in breaks[:_MAX_REPORTED])
        if len(breaks) > _MAX_REPORTED:
            shown += f", and {len(breaks) - _MAX_REPORTED} more"
        messages.append(
            f"{protid}: {len(breaks)} chain break(s) in the residue numbering ({shown}). "
            f"Neighbour exclusion is applied by position in the residue list rather than by residue "
            f"number, so residues flanking a break are treated as sequence neighbours.",
        )

    for message in messages:
        logger.warning(message)

    return messages
