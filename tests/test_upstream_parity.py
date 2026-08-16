"""Parity against the upstream ProteinCT reference implementation."""
import importlib.util
import re
import sys
from pathlib import Path

import numpy as np
import pytest
from conftest import INPUTS, PARAMS

UPSTREAM = Path(__file__).parent / "upstream"
UPSTREAM_SHA = "37e89951613d0bff5c33aafba666027c55c8dbda"

_AVAILABLE = (UPSTREAM / "functions" / "calculating" / "get_cmap.py").is_file()

pytestmark = pytest.mark.skipif(
    not _AVAILABLE,
    reason="upstream submodule not initialised; run: git submodule update --init tests/upstream",
)


def _upstream(func_name: str, relpath: str):
    """Load one upstream function by file path, under a private module name."""
    path = UPSTREAM / relpath
    spec = importlib.util.spec_from_file_location(f"_ct_upstream_{func_name}", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return getattr(module, func_name)

if _AVAILABLE:
    up_get_cmap = _upstream("get_cmap", "functions/calculating/get_cmap.py")
    up_get_matrix = _upstream("get_matrix", "functions/calculating/get_matrix.py")
    up_get_stats = _upstream("get_stats", "functions/calculating/get_stats.py")
    up_circuit_plot = _upstream("circuit_plot", "functions/plots/circuit_plot.py")
else:
    up_get_cmap = up_get_matrix = up_get_stats = up_circuit_plot = None

CASES = ["1crn", "1ubq", "1pnj"]


def _pdb(stem: str) -> Path:
    """Prefer the plugin's own fixture; fall back to upstream's input_files for 1PNJ."""
    local = INPUTS / f"{stem}.pdb"
    if local.is_file():
        return local
    return UPSTREAM / "input_files" / "pdb" / f"{stem}.pdb"


def _both_cmaps(stem: str):
    """Run the plugin's and upstream's get_cmap on the same chain of the same file."""
    from functions.importing.retrieve_chain import retrieve_chain

    pdb = _pdb(stem)

    chain_a, protid = retrieve_chain(pdb)
    chain_b, _ = retrieve_chain(pdb)

    mine = np.asarray(retrieve_and_map(chain_a, protid)[0])
    theirs = np.asarray(up_get_cmap(chain_b, level="chain", **PARAMS)[0])
    return mine, theirs, protid


def retrieve_and_map(chain, _protid):
    from functions.calculating.get_cmap import get_cmap

    return get_cmap(chain, level="chain", **PARAMS)

@pytest.mark.parametrize("stem", CASES)
def test_get_cmap_matches_upstream(stem):
    mine, theirs, _ = _both_cmaps(stem)
    assert mine.shape == theirs.shape, f"{stem}: {len(mine)} contacts vs upstream {len(theirs)}"
    assert np.array_equal(mine, theirs), f"{stem}: contact lists differ"


def test_get_cmap_reproduces_upstreams_published_1pnj_artefact():
    """Compare against upstream result, not just its code."""
    from functions.calculating.get_cmap import get_cmap
    from functions.importing.retrieve_chain import retrieve_chain

    expected_csv = UPSTREAM / "results" / "matrix" / "1pnj_A_mat.csv"
    header = expected_csv.read_text().splitlines()[0]
    expected = [(int(a), int(b)) for a, b in re.findall(r"\[(\d+) - (\d+)\]", header)]
    assert len(expected) == 63, f"upstream artefact changed shape: {len(expected)} contacts"

    chain, protid = retrieve_chain(_pdb("1pnj"))
    assert protid == "1pnj_A"
    idx, _numbering, protid, _ = get_cmap(chain, level="chain", **PARAMS)

    got = [(int(a), int(b)) for a, b in idx]
    assert got == expected, "contact list diverged from upstream's published 1PNJ result"


@pytest.mark.parametrize("stem", CASES)
def test_get_matrix_matches_upstream(stem):
    """The integer relation matrix must be identical."""
    from functions.calculating.get_matrix import get_matrix

    mine_idx, theirs_idx, protid = _both_cmaps(stem)

    my_mat, my_psx, _chainstats = get_matrix(mine_idx, protid)
    their_result = up_get_matrix(theirs_idx, protid)
    assert len(their_result) == 2, "upstream single-chain get_matrix should return (mat, psc)"
    their_mat, their_psc = their_result

    assert np.array_equal(my_mat, their_mat), f"{stem}: relation matrices differ"
    assert my_psx[0] == their_psc[0]
    assert my_psx[1:4] == their_psc[1:4], f"{stem}: P/S/X counts differ"
    assert my_psx[4:7] == their_psc[4:7], f"{stem}: P/S/X fractions differ"


@pytest.mark.parametrize("stem", CASES)
def test_get_stats_matches_upstream(stem):
    from functions.calculating.get_matrix import get_matrix
    from functions.calculating.get_stats import get_stats

    mine_idx, theirs_idx, protid = _both_cmaps(stem)
    my_mat, _, _ = get_matrix(mine_idx, protid)
    their_mat, _ = up_get_matrix(theirs_idx, protid)

    assert np.array_equal(get_stats(my_mat), up_get_stats(their_mat)), f"{stem}: stats differ"


@pytest.mark.parametrize("stem", CASES)
def test_circuit_plot_is_identical_to_upstream(stem, artifacts_dir):
    import matplotlib.pyplot as plt

    from functions.plots.circuit_plot import circuit_plot

    mine_idx, theirs_idx, protid = _both_cmaps(stem)

    def render(fn, index, out_name):
        plt.close("all")
        fn(index, protid, _numbering_for(stem))
        fig = plt.gcf()
        assert fig.get_axes(), f"{out_name}: nothing drawn"
        lines = [ln.get_xydata() for ln in fig.gca().get_lines()]
        colors = [ln.get_color() for ln in fig.gca().get_lines()]
        path = artifacts_dir / out_name
        fig.savefig(path, dpi=150, bbox_inches="tight", metadata={"Software": None})
        plt.close("all")
        return lines, colors, path

    my_lines, my_colors, my_png = render(circuit_plot, mine_idx, f"parity_{stem}_plugin.png")
    up_lines, up_colors, up_png = render(up_circuit_plot, theirs_idx, f"parity_{stem}_upstream.png")

    assert len(my_lines) == len(up_lines), (
        f"{stem}: {len(my_lines)} drawn elements vs upstream {len(up_lines)}"
    )
    assert my_colors == up_colors, f"{stem}: arc colours differ"
    for i, (a, b) in enumerate(zip(my_lines, up_lines, strict=True)):
        assert np.allclose(a, b, equal_nan=True), f"{stem}: element {i} vertices differ"

    assert my_png.read_bytes() == up_png.read_bytes(), (
        f"{stem}: rendered circuit plots differ; compare {my_png.name} and {up_png.name}"
    )


def _numbering_for(stem: str):
    from functions.calculating.get_cmap import get_cmap
    from functions.importing.retrieve_chain import retrieve_chain

    chain, _ = retrieve_chain(_pdb(stem))
    return get_cmap(chain, level="chain", **PARAMS)[1]
