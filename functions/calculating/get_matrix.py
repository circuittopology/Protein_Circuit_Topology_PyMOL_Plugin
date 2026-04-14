"""
Created on Mon May 24 17:00:09 2021

@author: DuaneM

Function creating a topological relationship matrix for a Residue contact map,
using either a single chain or a whole model.
"""
import logging

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def get_matrix(index: np.ndarray, protid: str) -> tuple[np.ndarray, list, dict]:  # noqa: PLR0912, PLR0915
    """
    Creates a topological relationship matrix for a residue contact map.

    Args:
        index (numpy.ndarray): Array containing contact indices.
        protid (str): Protein identifier.

    Returns:
        tuple: A tuple containing (matrix, stats, chainstats).
               For single chains, chainstats is an empty dict.
    """
    if index.shape == (0,):
        mat = np.zeros((len(index), len(index)),dtype = "int")
        psc = [protid,0,0,0]
        return mat,psc,{}
    #Determines whether index came from model or single chain
    if np.shape(index)[1] == 2:  # noqa: PLR2004
        #create a numerical and character matrix based on the amount of nonzero values found in the previous function
        mat = np.zeros((len(index), len(index)),dtype = "int")

        #Change the values based on the type of connection

        contact_p = 0
        contact_s = 0
        contact_x = 0

        for x in range(len(index)):
            i = index[x,0]
            j = index[x,1]
            for y in range(x+1,len(index)):
                k = index[y,0]
                _l = index[y,1]
                #series
                if (j < k):
                    contact_s += 1
                    mat[x, y]=1
                    mat[y, x]=1

                #parallel
                elif (i>k and j<_l):
                    contact_p += 1
                    mat[x, y]=2
                    mat[y, x]=3

                #5: CP
                #6: CP-1
                elif (i==k and j<_l):
                    mat[x, y]=5
                    mat[y, x]=6
                    contact_p += 1

                elif (i==k and _l<j) or (k>i and j==_l):
                    mat[x, y]=6
                    mat[y, x]=5
                    contact_p += 1

                elif(i>k and _l==j):
                    mat[x,y]=5
                    mat[y,x]=6
                    contact_p += 1
                #inverse parallel
                elif (k>i and _l<j):
                    contact_p += 1
                    mat[x, y]=3
                    mat[y, x]=2
                #CS
                elif (j ==k):
                    mat[x,y]=7
                    mat[y,x]=7
                    contact_s += 1
                #Cross
                if (k>i and k<j<_l) or (i>k and i< _l and j> _l):
                    contact_x += 1
                    mat[x, y]=4
                    mat[y, x]=4
        total = sum([contact_p,contact_s,contact_x])
        psc = [protid,contact_p,contact_s,contact_x,round(contact_p/total if total != 0 else 0,3),round(contact_s/total if total != 0 else 0,3),round(contact_x/total if total != 0 else 0,3)]

        return mat,psc,{}

    if np.shape(index)[1] == 4:  # noqa: PLR2004
        chainids = np.unique(index[:,2:])
        chainstats = {}
        for i in chainids:
            chainstats[i] = {"p":0,"s":0,"x":0,"i2":0,"i3":0,"i4":0,"t2":0,"t3":0,"l":0}

        mat = np.zeros((len(index), len(index)),dtype = "int")

        contact_p = 0
        contact_s = 0
        contact_x = 0
        contact_i2 = 0
        contact_i3 = 0
        contact_i4 = 0
        contact_t2 = 0
        contact_t3 = 0
        contact_l = 0

        for x in range(len(index)):
            chain1 = False
            i = index[x][0]
            j = index[x][1]
            chaini = index[x][2]
            chainj = index[x][3]

            if chaini == chainj:
                chain1 = True

            for y in range(x+1,len(index)):
                chain2 = False

                k = index[y][0]
                _l = index[y][1]
                chaink = index[y][2]
                chainl = index[y][3]

                set1 = {chaini,chainj}
                set2 = {chaink,chainl}

                if chaink == chainl:
                    chain2 = True

                if chain1 and chain2:
                    if chaini == chaink:
                        #series
                        if j < k:
                            contact_s += 1
                            mat[x,y] = 2
                            mat[y,x] = 2
                            chainstats[chaink]["s"] += 1

                        #parallel
                        elif (k < i and j < _l) or (i < k and _l < j):
                            contact_p += 1
                            mat[x,y] = 1
                            mat[y,x] = 1
                            chainstats[chaink]["p"] += 1

                        elif (i==k and j<_l) or (i==k and _l<j) or (k>i and j==_l) or (i>k and _l==j):
                            mat[x, y]=1
                            mat[y, x]=1
                            contact_p += 1
                            chainstats[chaink]["p"] += 1
                        #CS
                        elif j == k:
                            contact_s += 1
                            mat[x,y] = 2
                            mat[y,x] = 2
                            chainstats[chaink]["s"] += 1

                        #Cross
                        if (k>i and k<j<_l) or (i>k and i< _l and j> _l):
                            contact_x += 1
                            mat[x, y]=3
                            mat[y, x]=3
                            chainstats[chaink]["x"] += 1
                    #Independent
                    else:
                        contact_i2 += 1
                        mat[x,y] = 4
                        mat[y,x] = 4
                        chainstats[chaink]["i2"] += 1
                        chainstats[chainj]["i2"] += 1

                elif (chain1 and not set1.intersection(set2)) or (chain2 and not set1.intersection(set2)):
                    contact_i3 += 1
                    mat[x,y] = 4
                    mat[y,x] = 4
                    chainstats[chaini]["i3"] += 1
                    chainstats[chaink]["i3"] += 1
                    chainstats[chainl]["i3"] += 1

                #I - multiple chains
                elif not set1.intersection(set2):
                    contact_i4 += 1
                    mat[x,y] = 4
                    mat[y,x] = 4
                    chainstats[chaini]["i4"] += 1
                    chainstats[chainj]["i4"] += 1
                    chainstats[chaink]["i4"] += 1
                    chainstats[chainl]["i4"] += 1

                #T
                elif chain1 and set1.intersection(set2) :
                    contact_t2 += 1
                    mat[x,y] = 5
                    mat[y,x] = 5
                    chainstats[chaini]["t2"] += 1
                    chainstats[next(iter(set2-set1))]["t2"] += 1

                elif chain2 and set1.intersection(set2):
                    contact_t2 += 1
                    mat[x,y] = 5
                    mat[y,x] = 5
                    chainstats[chaink]["t2"] += 1
                    chainstats[next(iter(set1-set2))]["t2"] += 1
                elif ~chain1 and ~chain2 and len(set1.intersection(set2)) == 1:
                    contact_t3 += 1
                    mat[x,y] = 5
                    mat[y,x] = 5
                    chainstats[next(iter(set1.intersection(set2)))]["t3"] += 1
                    chainstats[next(iter(set2 - set1))]["t3"] += 1
                    chainstats[next(iter(set1 - set2))]["t3"] += 1
                #L
                elif ~chain1 and ~chain2 and set1 == set2:
                    contact_l += 1
                    mat[x,y] = 6
                    mat[y,x] = 6
                    chainstats[next(iter(set1.intersection(set2)))]["l"] += 1
                    chainstats[list(set1.intersection(set2))[1]]["l"] += 1
                else:
                    logger.error("error - %s %s %s %s %s %s %s %s", i, chaini, j, chainj, k, chaink, _l, chainl)

        stats = [protid,contact_p,contact_s,contact_x,contact_i2,contact_i3,contact_i4,contact_t2,contact_t3,contact_l]
        return mat,stats,chainstats

    msg = f"Unexpected index shape: {index.shape}. Expected 2 or 4 columns."
    raise ValueError(msg)
