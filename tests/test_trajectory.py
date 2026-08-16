"""Tests for utils.trajectory.export_frames_from_traj."""
import hashlib
import re
from pathlib import Path

from utils.trajectory import export_frames_from_traj


def ca_coords_hash(pdb_path: Path) -> str:
    """Hash only the CA coordinate columns: sensitive to coordinates, immune to headers."""
    h = hashlib.md5()  # noqa: S324
    for line in Path(pdb_path).read_text().splitlines():
        if line.startswith("ATOM") and line[12:16].strip() == "CA":
            h.update(line[30:54].encode())
    return h.hexdigest()


def model_record_count(pdb_path: Path) -> int:
    return len(re.findall(r"^MODEL", Path(pdb_path).read_text(), re.MULTILINE))


def test_export_writes_one_distinct_file_per_state(traj_case):
    """Every exported frame must differ."""
    case = traj_case(n_models=5)
    dialog = case.tab
    export_frames_from_traj(dialog)

    files = sorted(case.out.glob("*.pdb"))
    assert [f.name for f in files] == [f"frame_{i}.pdb" for i in range(1, 6)]

    assert {model_record_count(f) for f in files} == {0}
    assert len({ca_coords_hash(f) for f in files}) == 5, "exported frames are not distinct"

    assert dialog.traj_status_label.text() == f"Exported 5 frames to {case.out}"
    assert dialog.selected_traj_dir_multi == case.out

    assert (dialog.frame_selector_spinbox.minimum(),
            dialog.frame_selector_spinbox.maximum()) == (1, 5)


def test_single_state_object_exports_one_frame(traj_case):
    case = traj_case(n_models=1)
    export_frames_from_traj(case.tab)
    assert [p.name for p in case.out.glob("*.pdb")] == ["frame_1.pdb"]


def _configure_for_mat_export(tab, output_directory):
    """Multi-File tab set to export one relation matrix per unit of work, nothing else."""
    tab.cutoff_distance_multi.setValue(4.5)
    tab.min_contacts_multi.setValue(5)
    tab.exclude_neighbor_multi.setValue(3)
    for box in (
        tab.checkbox_circuit_multi, tab.checkbox_matrix_multi, tab.checkbox_stats_multi,
        tab.checkbox_export_cmap3_multi, tab.checkbox_export_psx_multi, tab.checkbox_plot_psx,
        tab.checkbox_length_filtering, tab.checkbox_energy_filtering,
    ):
        box.setChecked(False)
    tab.checkbox_export_matrix_multi.setChecked(True)
    tab.selected_output_dir_multi = str(output_directory)


def test_a_loaded_trajectory_is_analysed_without_exporting_any_frames(traj_case, tmp_path):
    """Batch analysis reads the trajectory's states straight from the PyMOL session."""
    from analysis.multiple_file_analysis import run_multi_analysis

    case = traj_case(n_models=4)
    tab = case.tab
    out = tmp_path / "matrices"
    _configure_for_mat_export(tab, out)

    tab.selected_input_dir_multi = None
    tab.selected_traj_dir_multi = None
    assert tab.get_multiple_values()["trajectory_object"] == case.name

    run_multi_analysis(tab)

    produced = sorted(p.name for p in out.glob("*.csv"))
    assert len(produced) == 4, f"expected one matrix per frame, got {produced}"
    assert produced == [f"{case.name}_frame_{i}_mat.csv" for i in range(1, 5)], produced

    from utils.helpers import temp_pdb_export
    from utils.validation import polymer_selection

    seen = set()
    for state in range(1, 5):
        with temp_pdb_export(polymer_selection(case.name), state=state, label="probe") as tmp:
            seen.add(ca_coords_hash(tmp))
    assert len(seen) == 4, "temp_pdb_export returns the same coordinates for every state"
