"""Small validation helpers for GUI-facing PyMOL workflows."""

from __future__ import annotations

import logging
from pathlib import Path

from pymol import cmd

logger = logging.getLogger(__name__)

SELECT_PLACEHOLDER = "Select a file."
STRUCTURE_SUFFIXES = {".pdb", ".cif"}
TRAJECTORY_SUFFIXES = {".xtc", ".dcd", ".trr", ".nc"}


def is_placeholder_object(obj_name: str | None) -> bool:
    """Return True when a combo-box value is not a real PyMOL object."""
    return not obj_name or obj_name == SELECT_PLACEHOLDER


def legalize_object_name(raw_name: str) -> str:
    """Return a PyMOL-safe object name for explicit load operations."""
    name = raw_name.strip() or "object"
    try:
        return str(cmd.get_legal_name(name))
    except Exception:  # noqa: BLE001
        logger.debug("Falling back to simple object-name normalization", exc_info=True)
        return name.replace(" ", "_")


def object_exists(obj_name: str | None) -> bool:
    """Return True when the named object exists in the current PyMOL session."""
    if is_placeholder_object(obj_name):
        return False
    assert obj_name is not None
    try:
        return obj_name in cmd.get_names("objects")
    except Exception:  # noqa: BLE001
        logger.debug("cmd.get_names failed; falling back to get_object_list", exc_info=True)
        try:
            return obj_name in cmd.get_object_list()
        except Exception:
            logger.exception("Unable to query PyMOL object list")
            return False


def object_selection(obj_name: str) -> str:
    """Return an exact object selection for a PyMOL object name."""
    return f"%{obj_name}"


def chain_selection(obj_name: str, chain_id: str) -> str:
    """Return a PyMOL selection for one chain of an object."""
    base_selection = object_selection(obj_name)
    if chain_id:
        return f"({base_selection}) and chain {chain_id}"
    return base_selection


def selection_has_atoms(selection: str) -> bool:
    """Return True when a PyMOL selection currently contains atoms."""
    try:
        return cmd.count_atoms(selection) > 0
    except Exception:
        logger.exception("Unable to count atoms for selection %s", selection)
        return False


def get_object_chains(obj_name: str) -> list[str]:
    """Return chains for an existing object, or an empty list on failure."""
    if not object_exists(obj_name):
        return []
    try:
        return list(cmd.get_chains(object_selection(obj_name)))
    except Exception:
        logger.exception("Unable to get chains for object %s", obj_name)
        return []


def validate_structure_file(path_like: str | Path) -> Path:
    """Validate a PDB/CIF file path and return it as a Path."""
    path = Path(path_like)
    if not path.exists():
        msg = f"The selected file does not exist: {path}"
        raise FileNotFoundError(msg)
    if not path.is_file():
        msg = f"The selected path is not a file: {path}"
        raise ValueError(msg)
    if path.suffix.lower() not in STRUCTURE_SUFFIXES:
        msg = "Please select a PDB or CIF file."
        raise ValueError(msg)
    return path


def validate_trajectory_file(path_like: str | Path) -> Path:
    """Validate a supported trajectory file path and return it as a Path."""
    path = Path(path_like)
    if not path.exists():
        msg = f"The selected trajectory file does not exist: {path}"
        raise FileNotFoundError(msg)
    if not path.is_file():
        msg = f"The selected trajectory path is not a file: {path}"
        raise ValueError(msg)
    if path.suffix.lower() not in TRAJECTORY_SUFFIXES:
        msg = "Please select an XTC, DCD, TRR, or NC trajectory file."
        raise ValueError(msg)
    return path


def list_structure_files(directory: str | Path) -> list[Path]:
    """Return sorted PDB/CIF files from a directory."""
    path = Path(directory)
    if not path.exists():
        msg = f"The input directory does not exist: {path}"
        raise FileNotFoundError(msg)
    if not path.is_dir():
        msg = f"The input path is not a directory: {path}"
        raise ValueError(msg)
    return sorted(
        file_path for file_path in path.iterdir()
        if file_path.is_file() and file_path.suffix.lower() in STRUCTURE_SUFFIXES
    )


def set_frame_spinbox_bounds(spinbox, file_count: int) -> None:
    """Set a 1-based frame spinbox range without creating invalid Qt ranges."""
    if file_count > 0:
        spinbox.setRange(1, file_count)
        spinbox.setValue(1)
    else:
        spinbox.setRange(0, 0)
        spinbox.setValue(0)


def selected_frame_file(files: list[Path], frame_index: int) -> Path:
    """Return the file for a 1-based frame index or raise a clear error."""
    if not files:
        msg = "No files are available for frame analysis."
        raise ValueError(msg)
    if frame_index < 1 or frame_index > len(files):
        msg = f"Frame {frame_index} is out of range. Choose a frame from 1 to {len(files)}."
        raise IndexError(msg)
    file_path = Path(files[frame_index - 1])
    if not file_path.exists():
        msg = f"The selected frame file no longer exists: {file_path}"
        raise FileNotFoundError(msg)
    return file_path
