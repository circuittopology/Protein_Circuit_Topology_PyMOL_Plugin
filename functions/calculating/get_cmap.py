"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

Function for creating a Residue-Residue based contact map for either a single chain or a whole model.
Note! this does not produce a contact map but a matrix of the non-zero values in that contact map. 
"""
from typing import List, Tuple, cast
from collections import Counter
import numpy as np
from Bio.PDB import Selection
from Bio.PDB.NeighborSearch import NeighborSearch
from Bio.PDB.Residue import Residue
from Bio.PDB.Atom import Atom
from Bio.PDB.Chain import Chain
from Bio.PDB.Model import Model

def get_cmap(
            chain: Chain | Model,
            level: str = 'chain',
            cutoff_distance: float = 4.5,
            cutoff_numcontacts: int = 5,
            exclude_neighbour: int = 3) -> Tuple[np.ndarray, np.ndarray, str, List[str]]:
    """
    Creates a residue-residue contact map (as a list of contacts) for a single chain or a whole model.

    Args:
        chain (Bio.PDB.Chain.Chain or Bio.PDB.Model.Model): The chain or model object to analyze.
        level (str, optional): 'chain' for single chain analysis, 'model' for whole model analysis. Defaults to 'chain'.
        cutoff_distance (float, optional): Maximum distance (in Angstroms) between atoms to consider a contact. Defaults to 4.5.
        cutoff_numcontacts (int, optional): Minimum number of atomic contacts required to define a residue-residue contact. Defaults to 5.
        exclude_neighbour (int, optional): Minimum sequence separation (in residues) to consider a contact. Defaults to 3.

    Returns:
        tuple: A tuple containing:
            - index (numpy.ndarray): Array of contact indices (and chain IDs if level='model').
            - numbering (numpy.ndarray): Array of residue numbers (and chain IDs if level='model').
            - protid (str): Protein identifier.
            - res_names (list): List of residue names.
    """
    if level == 'chain':

        #Unpack chain object into atoms and residues
        atom_list = cast(List[Atom], Selection.unfold_entities(chain,'A'))
        res_list = cast(List[Residue], Selection.unfold_entities(chain,'R'))

        res_names, numbering = [], []
        for res in res_list:
            res_names.append(res.get_resname())
            numbering.append(res.get_id()[1])

        #search for neighbouring atoms within specified distance
        ns = NeighborSearch(atom_list)
        all_neighbours = cast(List[Tuple[Atom, Atom]], ns.search_all(cutoff_distance,'A'))

        numbering = np.array(numbering)
        segment = np.array(range(len(numbering)))

        #transform atom contacts into residue contacts
        index_list = []
        for atompair in all_neighbours:
            parent0 = atompair[0].get_parent()
            parent1 = atompair[1].get_parent()
            assert parent0 is not None and parent1 is not None
            res1 = segment[numbering == parent0.id[1]][0]
            res2 = segment[numbering == parent1.id[1]][0]

            if abs(res1-res2) > exclude_neighbour:
                index_list.append((res1,res2))

        #sort residue contacts and check if they occur more
        # than the minimum set in cutoff_numcontacts
        index_list.sort()
        count = Counter(index_list)

        index = [values for values in count if count[values] >= cutoff_numcontacts]
        parent = chain.get_parent()
        assert parent is not None
        grandparent = parent.get_parent()
        assert grandparent is not None
        protid = grandparent.id + '_' + chain.id
        return np.array(index),numbering, protid,res_names

    #same as single chain analysis but unpacks whole model instead of single chain
    if level == 'model':

        atom_list_model = cast(List[Atom], Selection.unfold_entities(chain.get_parent(),'A'))
        res_list_model = cast(List[Residue], Selection.unfold_entities(chain.get_parent(),'R'))

        ns = NeighborSearch(atom_list_model)
        all_neighbours = cast(List[Tuple[Atom, Atom]], ns.search_all(cutoff_distance,'A'))

        res_names, numbering = [], []
        for res in res_list_model:
            res_names.append(res.get_resname())
            numbering.append([res.get_full_id()[2],res.get_full_id()[3][1]])

        numbering = np.array(numbering)

        segment = np.array(range(len(numbering)))

        index_list = []
        for atompair in all_neighbours:
            parent0 = atompair[0].get_parent()
            parent1 = atompair[1].get_parent()
            assert parent0 is not None and parent1 is not None
            res1 = segment[(numbering == [parent0.get_full_id()[2],str(parent0.get_full_id()[3][1])]).all(axis=1)][0]
            res2 = segment[(numbering == [parent1.get_full_id()[2],str(parent1.get_full_id()[3][1])]).all(axis=1)][0]
            chain1 = parent0.get_full_id()[2]
            chain2 = parent1.get_full_id()[2]

            if abs(res1-res2) > exclude_neighbour:
                index_list.append((res1,res2,chain1,chain2))

        index_list.sort()
        index_list.sort(key= lambda x : x[2:4])

        count = Counter(index_list)

        index = [values for values in count if count[values] >= cutoff_numcontacts]
        parent = chain.get_parent()
        assert parent is not None
        grandparent = parent.get_parent()
        assert grandparent is not None
        protid = grandparent.id

        return np.array(index),numbering,protid,res_names

    raise ValueError(f"Invalid level: '{level}'. Expected 'chain' or 'model'.")