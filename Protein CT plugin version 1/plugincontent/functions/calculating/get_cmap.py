"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

Function for creating a Residue-Residue based contact map for either a single chain or a whole model.
Note! this does not produce a contact map but a matrix of the non-zero values in that contact map. 
"""

from typing import Tuple, List

from Bio.PDB import Selection, NeighborSearch
from Bio.PDB.Chain import Chain
from collections import Counter
import numpy as np

def get_cmap(
            chain: Chain,
            level: str = 'chain',
            cutoff_distance: float = 4.5,
            cutoff_numcontacts: int = 5,        
            exclude_neighbour: int = 3) -> Tuple[np.ndarray, np.ndarray, str, List[str]]:
    """
    Creates a residue-residue contact map for a given chain or model.
    
    Args:
        chain: The biopython Chain object.
        level: Either 'chain' or 'model' to calculate contacts for.
        cutoff_distance: Maximum distance to consider atoms as neighbours.
        cutoff_numcontacts: Minimum number of atom contacts to consider a residue pair as a contact.
        exclude_neighbour: Minimum sequence separation to exclude local contacts.
        
    Returns:
        Tuple containing:
            - Array of contact indices.
            - Array of residue numbering.
            - Protein ID string.
            - List of residue names.
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
        
        numbering_arr = np.array(numbering)
        segment = np.array(range(len(numbering_arr)))

        #transform atom contacts into residue contacts
        index_list = []
        for atompair in all_neighbours:
            res1 = segment[numbering_arr == atompair[0].get_parent().id[1]][0]
            res2 = segment[numbering_arr == atompair[1].get_parent().id[1]][0]

            if abs(res1-res2) > exclude_neighbour:
                index_list.append((res1,res2))

        #sort residue contacts and check if they occur more than the minimum set in cutoff_numcontacts
        index_list.sort()
        count = Counter(index_list)

        index = [values for values in count if count[values] >= cutoff_numcontacts]
        protid = chain.get_parent().get_parent().id + '_' + chain.id
        return np.array(index), numbering_arr, protid, res_names
        
    #same as single chain analysis but unpacks whole model instead of single chain
    if level == 'model':

        atom_list_model = Selection.unfold_entities(chain.get_parent(),'A')
        res_list_model = Selection.unfold_entities(chain.get_parent(),'R')

        ns = NeighborSearch(atom_list_model)
        all_neighbours = ns.search_all(cutoff_distance,'A')

        res_names, numbering_model = [], []
        for res in res_list_model:
            res_names.append(res.get_resname())
            numbering_model.append([res.get_full_id()[2],res.get_full_id()[3][1]])

        numbering_arr_model = np.array(numbering_model)

        segment = np.array(range(len(numbering_arr_model)))
            
        index_list_model = []
        for atompair in all_neighbours:
            res1 = segment[(numbering_arr_model == [atompair[0].get_parent().get_full_id()[2],str(atompair[0].get_parent().get_full_id()[3][1])]).all(axis=1)][0]
            res2 = segment[(numbering_arr_model == [atompair[1].get_parent().get_full_id()[2],str(atompair[1].get_parent().get_full_id()[3][1])]).all(axis=1)][0]
            chain1 = atompair[0].get_parent().get_full_id()[2]
            chain2 = atompair[1].get_parent().get_full_id()[2]

            if abs(res1-res2) > exclude_neighbour:
                index_list_model.append((res1,res2,chain1,chain2))
                
        index_list_model.sort()
        index_list_model.sort(key= lambda x : x[2:4])
        
        count_model = Counter(index_list_model)

        index_model = [values for values in count_model if count_model[values] >= cutoff_numcontacts]
        protid = chain.get_parent().get_parent().id
        
        return np.array(index_model), numbering_arr_model, protid, res_names
    
    return np.array([]), np.array([]), "", []
