import numpy as np

from utils.topology import get_topology_vector


def get_folding_score(
    mat: np.ndarray,
    index: np.ndarray,
    numbering: np.ndarray
) -> float:
    """
    Calculate the folding score based on the given relations, using topology data.

    The score is the sum of the mean per-residue densities for parallel,
    series, and crossover contact types.

    Args:
        mat (numpy.ndarray): The topological relationship matrix.
        index (numpy.ndarray): Array of contact indices.
        numbering (list or numpy.ndarray): List of residue numbers/identifiers.

    Returns:
        float: The calculated folding score.
    """
    parallel_relations = get_topology_vector(mat, index, 'P', numbering)
    series_relations = get_topology_vector(mat, index, 'S', numbering)
    crossover_relations = get_topology_vector(mat, index, 'X', numbering)

    avg_parallel = np.mean(parallel_relations) if len(parallel_relations) > 0 else 0.0
    avg_series = np.mean(series_relations) if len(series_relations) > 0 else 0.0
    avg_crossover = np.mean(crossover_relations) if len(crossover_relations) > 0 else 0.0

    folding_score = float(avg_parallel + avg_series + avg_crossover)

    return folding_score