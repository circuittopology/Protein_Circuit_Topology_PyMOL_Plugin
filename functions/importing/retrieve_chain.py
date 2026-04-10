"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

Function for creating the chain object used in Bio.PDB and all the functions. Can specify which chain

"""
import warnings

from Bio import BiopythonWarning
from Bio.PDB import MMCIFParser, PDBParser
from Bio.PDB.Chain import Chain


def retrieve_chain(input_file: str, chainid: int | str = 0) -> tuple[Chain, str]:  # noqa: PLR0912
    """
    Retrieves a specific chain from a PDB or MMCIF file.

    Args:
        input_file (str): Path to the input PDB or MMCIF file.
        chainid (int or str, optional): The chain ID to retrieve. Can be an integer index or a string ID. Defaults to 0.

    Returns:
        tuple: A tuple containing the chain object (Bio.PDB.Chain.Chain) and the protein ID (str).
    """
    # determines which format is used
    if input_file.endswith("cif"):
        input_filepath = input_file
        # Supress harmless warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", BiopythonWarning)
            # Import the protein data
            structure = MMCIFParser().get_structure(input_file.replace(".cif", ""), input_filepath)
    else:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", BiopythonWarning)

            input_filepath = input_file
            # import protein data
            structure = PDBParser(PERMISSIVE=True).get_structure(input_file.replace(".pdb", ""), input_filepath)

    if structure:
        model = structure[0]
    else:
        msg = f"No structure found in the input file: {input_file}"
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

    return chain, protid
