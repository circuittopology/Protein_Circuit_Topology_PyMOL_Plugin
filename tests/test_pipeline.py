"""End-to-end and regression tests for the Protein Circuit Topology plugin."""
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from conftest import (
    EXPECTED,
    EXPECTED_COMMANDS,
    INPUTS,
    PARAMS,
    configure_local,
    configure_multi_file,
    configure_single_file,
)

CASES = ["1crn", "1ubq"]


def _load(cmd, stem: str) -> str:
    """Load a fixture exactly as a user would - waters and all."""
    path = INPUTS / f"{stem}.pdb"
    assert path.exists(), f"missing fixture {path}"
    cmd.load(str(path), stem)
    return stem


def _select_object(dialog, tab, combo_name: str, obj: str):
    """Populate the tab's object dropdown from the live session and select `obj`."""
    dialog.pymol_objects.refresh()
    combo = getattr(tab, combo_name)
    assert obj in [combo.itemText(i) for i in range(combo.count())], (
        f"{obj} did not appear in {combo_name} after a refresh"
    )
    combo.setCurrentText(obj)
    return tab


def _csvs(directory: Path) -> dict[str, str]:
    return {p.name: p.read_text(encoding="utf-8") for p in sorted(directory.glob("*.csv"))}


def _compare(produced: Path, expected: Path, update: bool) -> None:
    """Compare produced CSVs against the committed reference set."""
    got = _csvs(produced)
    assert got, f"the pipeline produced no CSV files in {produced}"

    if update:
        if expected.exists():
            shutil.rmtree(expected)
        expected.mkdir(parents=True)
        for name, text in got.items():
            (expected / name).write_text(text, encoding="utf-8", newline="")
        pytest.skip(f"regenerated {len(got)} reference file(s) in {expected}")

    assert expected.exists(), f"no reference outputs at {expected}; run pytest --update-expected"
    want = _csvs(expected)
    assert want, f"reference directory {expected} is empty"
    assert set(got) == set(want), f"file set differs: produced {sorted(got)} vs expected {sorted(want)}"

    for name in sorted(want):
        g = got[name].replace("\r\n", "\n")
        w = want[name].replace("\r\n", "\n")
        if g == w:
            continue
        if name.endswith("psxresults.csv"):
            gd = pd.read_csv(produced / name)
            wd = pd.read_csv(expected / name)
            pd.testing.assert_frame_equal(gd, wd, check_exact=False, rtol=1e-6)
            continue

        gl, wl = g.splitlines(), w.splitlines()
        assert len(gl) == len(wl), f"{name}: {len(gl)} lines produced, {len(wl)} expected"
        for i, (a, b) in enumerate(zip(gl, wl, strict=True), 1):
            assert a == b, f"{name} line {i}:\n  produced {a}\n  expected {b}"

def test_plugin_registers_all_commands(pymol_clean):
    """All 15 cmd.extend commands are reachable after registration."""
    missing = [name for name in EXPECTED_COMMANDS if name not in pymol_clean.keyword]
    assert not missing, f"commands absent from cmd.keyword: {missing}"

@pytest.mark.parametrize("stem", CASES)
def test_flow_single_file(stem, pipeline_env):
    """Single-File Analysis: PDB in, contact map and relation matrix out."""
    env = pipeline_env
    obj = _load(env.cmd, stem)
    tab = _select_object(env.dialog, env.dialog.single_file_tab, "dropdown_objects", obj)
    configure_single_file(tab, env.out)
    tab.run_standard_analysis()
    _compare(env.out, EXPECTED / f"single_{stem}", env.update)


def test_flow_multi_file(pipeline_env):
    """Multi-File Analysis: a directory of structures in, psxresults.csv out."""
    env = pipeline_env
    out = env.out / "out"
    tab = env.dialog.multi_file_tab
    configure_multi_file(tab, INPUTS, out)
    tab.run_multi_analysis()
    _compare(out, EXPECTED / "multi", env.update)


def test_flow_local_ct(pipeline_env):
    """Local Circuit Topology: one chain in, contact map and relation matrix out."""
    env = pipeline_env
    obj = _load(env.cmd, "1ubq")
    tab = _select_object(env.dialog, env.dialog.local_tab, "local_dropdown_objects", obj)
    tab.chain_combo_box.setCurrentText("A")
    configure_local(tab, env.out, res_id=10)
    tab.run_local_ct()
    _compare(env.out, EXPECTED / "local_1ubq", env.update)

def test_pymol_integration_commands(pymol_clean):
    """The utils/ layer: topology vector, folding score, and b-factor colouring."""
    from functions.calculating.get_cmap import get_cmap
    from functions.calculating.get_matrix import get_matrix
    from functions.importing.retrieve_chain import retrieve_chain
    from utils.folding_score import get_folding_score
    from utils.topology import color_by_topology, get_topology_vector

    obj = _load(pymol_clean, "1ubq")
    chain, protid = retrieve_chain(INPUTS / "1ubq.pdb")
    idx, numbering, protid, _ = get_cmap(chain, level="chain", **PARAMS)
    mat, _psx, _ = get_matrix(idx, protid)

    for kind in ("P", "S", "X"):
        vec = get_topology_vector(mat, idx, kind, numbering)
        assert vec is not None, f"no topology vector for {kind}"
        assert len(vec) == len(numbering), f"{kind}: {len(vec)} values for {len(numbering)} residues"
        assert np.all(np.asarray(vec) >= 0)

    assert get_topology_vector(mat, idx, "NOPE", numbering) is None

    score = get_folding_score(mat, idx, numbering)
    assert isinstance(score, float)
    assert score > 0, "1UBQ should have a non-zero folding score"

    vec = get_topology_vector(mat, idx, "X", numbering)
    assert vec is not None
    color_by_topology(molecule_name=obj, topology_vector=vec, numbering=numbering, topology_type="X")
    bfactors = []
    pymol_clean.iterate(obj, "bfactors.append(b)", space={"bfactors": bfactors})
    assert bfactors, "no atoms to read B-factors from"
    assert any(b != 0 for b in bfactors), "colouring wrote no B-factor values"

    from utils.non_polymer import non_polymer_counts

    assert non_polymer_counts(obj)["HOH"] > 0, "1UBQ's waters were removed from the session"

def test_plot_functions_render_headless():
    """All five plot commands produce a non-empty figure under the Agg backend."""
    import matplotlib
    import matplotlib.pyplot as plt

    assert matplotlib.get_backend().lower() == "agg"

    from functions.calculating.get_cmap import get_cmap
    from functions.calculating.get_matrix import get_matrix
    from functions.calculating.get_stats import get_stats
    from functions.importing.retrieve_chain import retrieve_chain
    from functions.plots.circuit_plot import circuit_plot
    from functions.plots.matrix_plot import matrix_plot
    from functions.plots.stats_plot import stats_plot

    chain, protid = retrieve_chain(INPUTS / "1crn.pdb")
    idx, numbering, protid, _ = get_cmap(chain, level="chain", **PARAMS)
    mat, psx, _ = get_matrix(idx, protid)

    for name, call in (
        ("circuit_plot", lambda: circuit_plot(index=idx, protid=protid, numbering=numbering)),
        ("matrix_plot", lambda: matrix_plot(mat=mat, protid=protid)),
        ("stats_plot", lambda: stats_plot(get_stats(mat), psx, protid)),
    ):
        plt.close("all")
        call()
        fig = plt.gcf()
        assert fig.get_axes(), f"{name} drew nothing"
        plt.close("all")

def test_ctdialog_constructs_offscreen():
    """CTDialog builds, lays out and rasterises under QT_QPA_PLATFORM=offscreen."""
    from PyQt5.QtWidgets import QApplication, QPushButton

    app = QApplication.instance() or QApplication(sys.argv[:1])

    from gui_class import CTDialog

    dialog = CTDialog()
    try:
        assert dialog.tab_widget.count() == 3, f"expected 3 tabs, got {dialog.tab_widget.count()}"
        titles = [dialog.tab_widget.tabText(i) for i in range(3)]
        assert all(titles), f"a tab has no title: {titles}"

        assert "Local Circuit Topology" in titles

        dialog.show()
        app.processEvents()
        pixmap = dialog.grab()
        assert not pixmap.isNull(), "dialog rendered a null pixmap"
        assert pixmap.width() > 0 and pixmap.height() > 0

        buttons = dialog.findChildren(QPushButton)
        assert buttons, "dialog has no buttons"

        info = [b for b in buttons if b.text() == "ⓘ"]
        action = [b for b in buttons if b.text() and b.text() != "ⓘ"]
        assert info, "expected the parameter info buttons to exist"
        assert action, "expected action buttons to exist"

        untooltipped = [i for i, b in enumerate(info) if not b.toolTip()]
        assert not untooltipped, f"info buttons without a tooltip at indices {untooltipped}"

        unwired = [b.text() for b in action if b.receivers(b.clicked) == 0]
        assert not unwired, f"action buttons with no clicked handler: {unwired}"
    finally:
        dialog.close()
        dialog.deleteLater()
        app.processEvents()

def test_requirements_covers_all_imports():
    """Every third-party module the plugin imports must be declared in requirements.yml."""
    from initialization_checks import (
        REQUIREMENTS_FILE,
        _is_package_available,
        requirement_specs,
    )

    declared = list(requirement_specs(REQUIREMENTS_FILE))
    assert declared, "requirements.yml declared nothing"

    needed = {"numpy", "pandas", "matplotlib", "biopython"}
    missing = sorted(needed - {d.lower() for d in declared})
    assert not missing, f"imported but not declared in requirements.yml: {missing}"

    unresolvable = [d for d in declared if not _is_package_available(d)]
    assert not unresolvable, f"declared but not importable after mapping: {unresolvable}"
