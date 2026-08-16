"""Shared fixtures for the Protein Circuit Topology plugin test suite."""
import importlib.util
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import ClassVar
from unittest.mock import MagicMock

REPO_ROOT = Path(__file__).resolve().parents[1]

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("MPLBACKEND", "Agg")

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest

DATA = Path(__file__).parent / "data"
INPUTS = DATA / "inputs"
EXPECTED = DATA / "expected"
PARAMS = {"cutoff_distance": 4.5, "cutoff_numcontacts": 5, "exclude_neighbour": 3}

EXPECTED_COMMANDS = (
    "circuit_plot", "matrix_plot", "stats_plot", "matrix_plot_model", "local_topology_plot",
    "get_cmap", "get_matrix", "get_stats", "energy_cmap", "length_filter", "local_ct",
    "retrieve_chain", "export_psx", "export_cmap3", "export_mat",
    "get_topology_vector", "color_by_topology", "get_folding_score",
)

_QMSG_MODULES = (
    "analysis.single_file_analysis",
    "analysis.multiple_file_analysis",
    "analysis.local_ct_analysis",
    "analysis.single_frame_analysis",
    "analysis.visualization",
    "utils.helpers",
    "utils.trajectory",
    "utils.directory",
    "utils.non_polymer",
)

_QFILE_MODULES = (
    "utils.trajectory",
    "utils.directory",
)


class _RaisingMessageBox:
    """Stand-in for QMessageBox."""
    Yes, No, Warning = 0x4000, 0x10000, 2

    def __new__(cls, *_a, **_kw):
        """QMessageBox(parent) -> an inert mock, so setText/addButton/exec_ all no-op."""
        return MagicMock()

    @staticmethod
    def warning(_parent, title, text, *_a, **_kw):
        msg = f"QMessageBox.warning({title!r}): {text}"
        raise AssertionError(msg)

    @staticmethod
    def critical(_parent, title, text, *_a, **_kw):
        msg = f"QMessageBox.critical({title!r}): {text}"
        raise AssertionError(msg)

    @staticmethod
    def information(*_a, **_kw):
        """Success notifications are not failures ("Processed 2 of 2 files")."""

    @staticmethod
    def question(*_a, **_kw):
        return _RaisingMessageBox.Yes


class _FakeFileDialog:
    """Stand-in for QFileDialog."""

    directory: ClassVar[str] = ""
    open_file: ClassVar[str] = ""

    @staticmethod
    def getExistingDirectory(*_a, **_kw):
        return _FakeFileDialog.directory

    @staticmethod
    def getOpenFileName(*_a, **_kw):
        return (_FakeFileDialog.open_file, "")


def _set_common_params(distance, contacts, neighbours):
    """The three contact-map spin boxes every tab carries, set to PARAMS."""
    distance.setValue(PARAMS["cutoff_distance"])
    contacts.setValue(PARAMS["cutoff_numcontacts"])
    neighbours.setValue(PARAMS["exclude_neighbour"])


def configure_single_file(tab, output_directory):
    """Single-File Analysis tab: both CSV exports on, every plot off."""
    _set_common_params(tab.cutoff_distance_spin, tab.min_contacts_spin, tab.exclude_neighbor_spin)
    for box in (tab.checkbox_circuit_plot, tab.checkbox_folding_score, tab.checkbox_matrix_plot):
        box.setChecked(False)
    tab.checkbox_export_cmap3.setChecked(True)
    tab.checkbox_export_matrix.setChecked(True)
    tab.selected_output_dir = str(output_directory)


def configure_multi_file(tab, directory, output_directory):
    """Multi-File Analysis tab: PSX export only, no filtering."""
    _set_common_params(tab.cutoff_distance_multi, tab.min_contacts_multi, tab.exclude_neighbor_multi)
    for box in (
        tab.checkbox_circuit_multi, tab.checkbox_matrix_multi, tab.checkbox_stats_multi,
        tab.checkbox_export_cmap3_multi, tab.checkbox_export_matrix_multi, tab.checkbox_plot_psx,
        tab.checkbox_length_filtering, tab.checkbox_energy_filtering,
    ):
        box.setChecked(False)
    tab.checkbox_export_psx_multi.setChecked(True)
    tab.selected_input_dir_multi = str(directory)
    tab.selected_traj_dir_multi = None
    tab.selected_output_dir_multi = str(output_directory)


def configure_local(tab, output_directory, res_id=10):
    """Local Circuit Topology tab: both CSV exports on, plot off."""
    _set_common_params(
        tab.cutoff_distance_local, tab.min_contacts_local, tab.exclude_neighbor_local,
    )
    tab.dropdown_contact_type.setCurrentText("Cross (X)")

    assert tab.dropdown_contact_type.currentText() == "Cross (X)"

    tab.box_res_id.setValue(res_id)
    tab.checkbox_local_ct.setChecked(True)
    tab.checkbox_local_ct_plot.setChecked(False)
    tab.checkbox_local_cmap3.setChecked(True)
    tab.checkbox_local_matrix.setChecked(True)
    tab.selected_output_dir_local = str(output_directory)


def pytest_addoption(parser):
    parser.addoption(
        "--update-expected",
        action="store_true",
        default=False,
        help="Regenerate tests/data/expected/ from the current code instead of comparing "
             "against it. Review diff before committing.",
    )


@pytest.fixture(scope="session", autouse=True)
def _pymol_session():
    """Start headless PyMOL once per session and register the plugin's commands."""
    missing = [m for m in ("numpy", "pandas", "matplotlib", "Bio", "PyQt5")
               if importlib.util.find_spec(m) is None]
    if missing:
        pytest.exit(f"Test environment is missing {missing}; refusing to run because the "
                    f"plugin would try to conda-install them.", returncode=1)

    import pymol

    pymol.finish_launching(["pymol", "-qc"])

    from initialization_checks import register_pymol_functions

    register_pymol_functions()

    yield

    from pymol import cmd

    cmd.reinitialize()


@pytest.fixture
def pymol_clean():
    """Give test a fresh PyMOL session, handing back cmd."""
    from pymol import cmd

    cmd.reinitialize()

    yield cmd

    cmd.reinitialize()


@pytest.fixture
def no_dialogs(monkeypatch):
    """Neutralise every blocking Qt surface the plugin can reach."""
    _FakeFileDialog.directory = ""
    _FakeFileDialog.open_file = ""

    for mod_name in _QMSG_MODULES:
        module = importlib.import_module(mod_name)
        monkeypatch.setattr(module, "QMessageBox", _RaisingMessageBox, raising=False)

    for mod_name in _QFILE_MODULES:
        module = importlib.import_module(mod_name)
        monkeypatch.setattr(module, "QFileDialog", _FakeFileDialog, raising=False)

    monkeypatch.setattr("analysis.single_file_analysis.show_folding_score_dialog",
                        lambda *_a, **_kw: None)

    return _RaisingMessageBox


def write_multimodel_pdb(dest, n_models=5):
    """Build a multi-MODEL PDB from 1crn, shifting x by 0.5 A per model."""
    dx = 0.5
    src = INPUTS / "1crn.pdb"
    atoms = [ln for ln in src.read_text().splitlines() if ln.startswith(("ATOM", "HETATM"))]
    dest = Path(dest)
    with dest.open("w") as fh:
        for m in range(1, n_models + 1):
            fh.write(f"MODEL     {m:4d}\n")
            for ln in atoms:
                fh.write(ln[:30] + f"{float(ln[30:38]) + dx * m:8.3f}" + ln[38:] + "\n")
            fh.write("ENDMDL\n")
        fh.write("END\n")

    return dest


def write_gapped_pdb(dest, drop=(25, 41), src_stem="1ubq"):
    """Build a PDB with a stretch of residues excised, leaving the numbering discontinuous."""
    src = INPUTS / f"{src_stem}.pdb"
    dropped = set(range(*drop))
    kept = [
        ln for ln in src.read_text().splitlines()
        if not (ln.startswith(("ATOM", "HETATM")) and int(ln[22:26]) in dropped)
    ]
    dest = Path(dest)
    dest.write_text("\n".join(kept) + "\n")

    return dest

@pytest.fixture
def pipeline_env(pymol_clean, no_dialogs, ct_dialog, tmp_path, request):
    """Everything a flow test needs: clean session, real dialog, output dir, dialogs muted."""
    return SimpleNamespace(
        cmd=pymol_clean,
        dialog=ct_dialog,
        out=tmp_path,
        update=bool(request.config.getoption("--update-expected")),
    )


@pytest.fixture(scope="session")
def artifacts_dir():
    """Output _artifacts dir for session of tests."""
    d = Path(__file__).parent / "_artifacts"
    d.mkdir(parents=True, exist_ok=True)

    return d


@pytest.fixture
def traj_case(pymol_clean, no_dialogs, tmp_path, ct_dialog):
    """A loaded multi-state object, its PyMOL name, and an output dir wired into the file chooser."""
    def _make(n_models=5):
        name = pymol_clean.get_unused_name("traj")
        mol = write_multimodel_pdb(tmp_path / "traj.pdb", n_models=n_models)
        pymol_clean.load(str(mol), name)
        assert pymol_clean.count_states(f"%{name}") == n_models

        out = tmp_path / "frames"
        _FakeFileDialog.directory = str(out)

        tab = ct_dialog.multi_file_tab
        tab.traj_mol_path = str(mol)
        tab.traj_xtc_path = "unused.xtc"
        tab.protein_name = name

        return SimpleNamespace(
            mol=mol, name=name, out=out, tab=tab, dialogs=_FakeFileDialog,
        )

    return _make


@pytest.fixture(scope="session")
def qapp():
    """One QApplication for session."""
    from PyQt5.QtWidgets import QApplication

    return QApplication.instance() or QApplication(sys.argv[:1])


@pytest.fixture
def ct_dialog(qapp):
    """CTDialog, offscreen, with polling timer stopped."""
    from gui_class import CTDialog

    dlg = CTDialog()
    dlg.pymol_objects.stop()

    yield dlg

    dlg.close()
    dlg.deleteLater()
