import numpy as np

from utils.relations import get_relation_type_vector


def get_folding_score(
    mat: np.ndarray,
    index: np.ndarray,
    numbering: np.ndarray,
) -> float:
    """
    Calculate the folding score based on the given relations, using topology data.

    The score is the sum of the mean per-residue participation in Parallel,
    Series and Cross relations.

    Args:
        mat (np.ndarray): The topological relationship matrix.
        index (np.ndarray): Array of contact indices.
        numbering (np.ndarray): Array of residue numbers/identifiers.

    Returns:
        float: The calculated folding score.
    """
    parallel_relations = get_relation_type_vector(mat, index, "P", numbering)
    series_relations = get_relation_type_vector(mat, index, "S", numbering)
    cross_relations = get_relation_type_vector(mat, index, "X", numbering)

    avg_parallel = np.mean(parallel_relations) if len(parallel_relations) > 0 else 0.0
    avg_series = np.mean(series_relations) if len(series_relations) > 0 else 0.0
    avg_cross = np.mean(cross_relations) if len(cross_relations) > 0 else 0.0

    return float(avg_parallel + avg_series + avg_cross)
