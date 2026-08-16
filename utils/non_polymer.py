"""Reporting non-polymer content, without touching it."""
import logging
from collections import Counter

from pymol import cmd

from utils.validation import object_exists, object_selection

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

_MAX_NAMED_RESIDUES = 4

def non_polymer_counts(obj_name: str) -> Counter:
    """Residue-name histogram of the non-polymer atoms in one object. Empty when there are none."""
    if not object_exists(obj_name):
        return Counter()
    names: list[str] = []
    try:
        cmd.iterate(
            f"({object_selection(obj_name)}) and not polymer",
            "names.append(resn)",
            space={"names": names},
        )
    except Exception:
        logger.debug("Could not inspect non-polymer atoms of %s", obj_name, exc_info=True)
        return Counter()
    return Counter(names)


def report_excluded_atoms(obj_name: str) -> str:
    """Log what analysis will ignore. Returns the message or empty string."""
    counts = non_polymer_counts(obj_name)
    if not counts:
        return ""

    ranked = counts.most_common()
    named = ", ".join(f"{n} {resn}" for resn, n in ranked[:_MAX_NAMED_RESIDUES])
    if len(ranked) > _MAX_NAMED_RESIDUES:
        named += f", +{len(ranked) - _MAX_NAMED_RESIDUES} more"

    notice = (
        f"Excluded {sum(counts.values())} non-polymer atom(s) from the analysis of "
        f"'{obj_name}' ({named}). '{obj_name}' itself is unchanged."
    )

    logger.info(notice)

    return notice
