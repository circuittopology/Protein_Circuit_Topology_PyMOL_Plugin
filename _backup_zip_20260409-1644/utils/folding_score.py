from .topology import get_topology_vector
import numpy as np

def get_folding_score(mat: np.ndarray, index: np.ndarray, numbering: np.ndarray) -> float:
    """
    Calculate the folding score based on the given relations, using topology data.
    
    Args:
        mat: Topological relationships matrix.
        index: Contact indices.
        numbering: Residue numbering array.
        
    Returns:
        The calculated folding score.
    """
    # Get the topology vectors for parallel, series, and crossover relations
    parallel_relations = get_topology_vector(mat, index, 'P', numbering)
    series_relations = get_topology_vector(mat, index, 'S', numbering)
    crossover_relations = get_topology_vector(mat, index, 'X', numbering)

    # Calculate averages for P, S, and X across the trajectoryif len(parallel_relations) > 0:
    if len(parallel_relations) > 0:
        avg_parallel = sum(parallel_relations) / len(parallel_relations)
    else:
        avg_parallel = 0

    print("avg_parallel:", avg_parallel)

    if len(series_relations) > 0:
        avg_series = sum(series_relations) / len(series_relations)
    else:
        avg_series = 0

    if len(crossover_relations) > 0:
        avg_crossover = sum(crossover_relations) / len(crossover_relations)
    else:
        avg_crossover = 0

    # Normalize the P, S, X values by their respective averages
    normalized_parallel = sum(parallel_relations) / avg_parallel if avg_parallel != 0 else 0
    normalized_series = sum(series_relations) / avg_series if avg_series != 0 else 0
    normalized_crossover = sum(crossover_relations) / avg_crossover if avg_crossover != 0 else 0

    # Folding score calculation
    folding_score = normalized_parallel + normalized_series + normalized_crossover

    print("Final folding_score:", folding_score)

    return folding_score