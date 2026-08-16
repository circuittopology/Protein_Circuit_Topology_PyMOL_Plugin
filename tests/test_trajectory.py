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
