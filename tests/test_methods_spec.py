"""
Executable version of documentation/METHODS.md.

Several of these tests pin behaviour that is IMPERFECT and inherited 1:1 from the reference ProteinCT
implementation. Deliberately not "fixed": the plugin's outputs must agree with ProteinCT's, thus changing
the arithmetic would break it. The plugin's contribution here is that affected structures are now detected
and reported instead of being silently mishandled.
"""
from itertools import pairwise

import numpy as np
import pytest
from conftest import INPUTS, PARAMS, write_gapped_pdb

from functions.calculating.get_cmap import get_cmap
from functions.importing.retrieve_chain import retrieve_chain, warn_about_numbering


def _chain(path):
    return retrieve_chain(path)

def test_waters_and_hetero_residues_are_dropped_at_parse_time():
    """Hetero residues never reach contact detection, whatever the PyMOL session still holds."""
    chain, _ = _chain(INPUTS / "1ubq.pdb")
    resnames = {res.get_resname() for res in chain}
    assert "HOH" not in resnames, "waters survived into the analysed chain"
    assert all(res.id[0] == " " for res in chain), "a hetero-flagged residue survived"


def test_hydrogens_are_not_filtered_out():
    """Contact detection uses ALL atoms present, not heavy atoms only."""
    import inspect

    source = inspect.getsource(get_cmap)
    assert "element" not in source and "hydrogen" not in source.lower(), (
        "get_cmap now filters by element; METHODS.md says it does not"
    )


def test_the_contact_criterion_counts_atom_pairs_per_residue_pair():
    """Raising the minimum atom-pair count can only ever remove contacts."""
    chain, _ = _chain(INPUTS / "1ubq.pdb")
    base, _, _, _ = get_cmap(chain, level="chain", **PARAMS)

    strict = dict(PARAMS, cutoff_numcontacts=PARAMS["cutoff_numcontacts"] + 5)
    fewer, _, _, _ = get_cmap(chain, level="chain", **strict)

    assert len(fewer) <= len(base)
    assert {tuple(c) for c in fewer} <= {tuple(c) for c in base}, "a stricter cut-off invented contacts"


def test_neighbour_exclusion_is_applied_by_list_position(tmp_path):
    """Sequence separation is measured in list positions, not residue numbers. INHERITED."""
    gapped = write_gapped_pdb(tmp_path / "gapped.pdb")
    chain, _ = _chain(gapped)
    numbers = [res.id[1] for res in chain]

    breaks = [(a, b) for a, b in pairwise(numbers) if b - a > 1]
    assert breaks, "fixture should contain a chain break"

    index, numbering, _, _ = get_cmap(chain, level="chain", **PARAMS)

    assert index.max() < len(numbering), "index holds residue numbers, not positions"

def test_a_chain_break_is_reported(tmp_path):
    gapped = write_gapped_pdb(tmp_path / "gapped.pdb")
    chain, protid = _chain(gapped)
    messages = warn_about_numbering(chain, protid)
    assert any("chain break" in m for m in messages), messages


def test_a_clean_structure_reports_nothing():
    """No false alarms on an ordinary complete structure."""
    for stem in ("1crn", "1ubq"):
        chain, protid = _chain(INPUTS / f"{stem}.pdb")
        assert warn_about_numbering(chain, protid) == [], f"{stem} triggered a spurious warning"

def test_protid_carries_the_chain_id_at_chain_level():
    """protid is '<file stem>_<chain id>', which is what every exported filename is built from."""
    chain, protid = _chain(INPUTS / "1ubq.pdb")
    assert protid == "1ubq_A"
    assert chain.id == "A"


@pytest.mark.parametrize("stem", ["1crn", "1ubq"])
def test_chain_level_returns_two_column_contacts(stem):
    """Single-chain analysis yields (residue_i, residue_j); model level adds chain columns."""
    chain, _ = _chain(INPUTS / f"{stem}.pdb")
    index, _, _, _ = get_cmap(chain, level="chain", **PARAMS)
    assert index.ndim == 2
    assert index.shape[1] == 2, f"chain level should give 2 columns, got {index.shape[1]}"
    assert np.issubdtype(index.dtype, np.integer)
