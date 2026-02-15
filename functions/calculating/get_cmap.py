"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

Function for creating a Residue-Residue based contact map for either a single chain or a whole model.
Note! this does not produce a contact map but a matrix of the non-zero values in that contact map. 
"""

from collections import Counter
from Bio.PDB import Selection,NeighborSearch, Chain
import numpy as np

def get_cmap(
            chain: Chain.Chain,
            level: str = 'chain',
            cutoff_distance: float = 4.5,
            cutoff_numcontacts: int = 5,
            exclude_neighbour: int = 3
    ) -> tuple[np.ndarray, np.ndarray, str, list[str]]:
    """
    Function that generates a Residue contact map for a single chain or a whole model.
    Note! returns of the indices of nonzero values in the contact map.

    Parameters
    chain : Bio.PDB.Chain.Chain
        Chain object created in the retrieve_chain() function.
    level : str
        specify level of contact map. ‘chain’ for single chain analysis and
        ‘model’ for multi-chain analysis.
    cutoff_distance : float
        maximum distance (Angstrom) between 2 atoms that will count as an
        atom-atom contact
    cutoff_numcontacts : int
        Minimum number of contacts between two residues to count as a
        residue contact
    exclude_neighbour : int
        Number of residue neighbors to exclude from contacts.
    
    Returns
    index : np.ndarray
        Array consisting out of the indices of the res-res contacts
    numbering : np.ndarray
        Original ID’s of each of the residues
    protid : str
        ID of the protein + the chain used. When ‘model’ option activated, no
        chain identifier in the protid.
    res_names : list[str]
        Three letter name code for each residue in the chain/model.
    """
    if level == 'chain':

        #Unpack chain object into atoms and residues
        atom_list = Selection.unfold_entities(chain,'A')
        res_list = Selection.unfold_entities(chain,'R')

        res_names, numbering = [], []
        for res in res_list:
            res_names.append(res.get_resname())
            numbering.append(res.get_id()[1])

        #search for neighbouring atoms within specified distance
        ns = NeighborSearch(atom_list)
        all_neighbours = ns.search_all(cutoff_distance,'A')

        numbering = np.array(numbering)
        segment = np.array(range(len(numbering)))

        #transform atom contacts into residue contacts
        index_list = []
        for atompair in all_neighbours:
            res1 = segment[numbering == atompair[0].get_parent().id[1]][0]
            res2 = segment[numbering == atompair[1].get_parent().id[1]][0]

            if abs(res1-res2) > exclude_neighbour:
                index_list.append((res1,res2))

        # sort residue contacts and check if they occur more than
        # the minimum set in cutoff_numcontacts
        index_list.sort()
        count = Counter(index_list)

        index = [values for values in count if count[values] >= cutoff_numcontacts]
        protid = chain.get_parent().get_parent().id + '_' + chain.id
        return np.array(index),numbering, protid,res_names

    #same as single chain analysis but unpacks whole model instead of single chain
    if level == 'model':

        atom_list_model = Selection.unfold_entities(chain.get_parent(),'A')
        res_list_model = Selection.unfold_entities(chain.get_parent(),'R')

        ns = NeighborSearch(atom_list_model)
        all_neighbours = ns.search_all(cutoff_distance,'A')

        res_names, numbering = [], []
        for res in res_list_model:
            res_names.append(res.get_resname())
            numbering.append([res.get_full_id()[2],res.get_full_id()[3][1]])

        numbering = np.array(numbering)

        segment = np.array(range(len(numbering)))

        index_list = []
        for atompair in all_neighbours:
            res1 = segment[(numbering == [atompair[0].get_parent().get_full_id()[2],str(atompair[0].get_parent().get_full_id()[3][1])]).all(axis=1)][0]
            res2 = segment[(numbering == [atompair[1].get_parent().get_full_id()[2],str(atompair[1].get_parent().get_full_id()[3][1])]).all(axis=1)][0]
            chain1 = atompair[0].get_parent().get_full_id()[2]
            chain2 = atompair[1].get_parent().get_full_id()[2]

            if abs(res1-res2) > exclude_neighbour:
                index_list.append((res1,res2,chain1,chain2))

        index_list.sort()
        index_list.sort(key= lambda x : x[2:4])

        count = Counter(index_list)

        index = [values for values in count if count[values] >= cutoff_numcontacts]
        protid = chain.get_parent().get_parent().id

        return np.array(index),numbering,protid,res_names
