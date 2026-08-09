import logging
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from pymol import cmd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout

from utils.config import INFO_BUTTON_STYLE

logger = logging.getLogger(__name__)


def update_chain_combo_box(self: Any) -> None:
    """
    Updates the chain combo box with the chains available in the currently selected object.

    Args:
        self: The main GUI class instance.
    """
    self.chain_combo_box.clear()
    self.chain_combo_box.addItems(self.curr_chain_residues.keys())

def make_info_button(tooltip: str) -> QPushButton:
    """
    Creates a small info button with a tooltip.

    Args:
        tooltip (str): The text to display in the tooltip.

    Returns:
        QPushButton: The configured info button.
    """
    btn = QPushButton("ⓘ")
    btn.setFixedWidth(20)
    btn.setFlat(True)
    btn.setStyleSheet(INFO_BUTTON_STYLE)
    btn.setToolTip(tooltip)
    return btn

@contextmanager
def temp_pdb_export(selection: str, state: int | None = None, label: str | None = None):
    """Save a PyMOL selection to a temporary PDB file, yield the path, then clean up."""
    safe = "".join(c if (c.isalnum() or c in "-_") else "_" for c in (label or "structure"))
    with tempfile.TemporaryDirectory(prefix="ct_export_") as tmpdir:
        tmp_path = Path(tmpdir) / f"{safe or 'structure'}.pdb"
        cmd.save(str(tmp_path), selection, state=state if state is not None else cmd.get_state())
        yield tmp_path


def make_param_row(label_text, tooltip, spinbox):
    """Create a standard parameter row layout with label, info button, and spinbox."""
    row = QHBoxLayout()
    row.addWidget(QLabel(label_text))
    row.addWidget(make_info_button(tooltip))
    row.addStretch()
    row.addWidget(spinbox)
    return row


def show_folding_score_dialog(parent: Any, chain: str, folding_score: float) -> None:
    """Show the CT folding score for a chain in a small, auto-sized pop-up dialog."""
    dialog = QDialog(parent)
    dialog.setWindowTitle("CT Folding Score")

    layout = QVBoxLayout()
    layout.setContentsMargins(24, 20, 24, 20)
    layout.setSpacing(12)

    title_label = QLabel(f"CT Folding Score — Chain {chain}")
    title_label.setAlignment(Qt.AlignCenter)
    title_label.setStyleSheet("font-size: 11pt; color: palette(mid);")
    layout.addWidget(title_label)

    score_label = QLabel(f"{folding_score:.4f}")
    score_label.setAlignment(Qt.AlignCenter)
    score_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
    score_label.setStyleSheet("font-size: 22pt; font-weight: bold;")
    layout.addWidget(score_label)

    button_row = QHBoxLayout()
    button_row.addStretch()
    ok_button = QPushButton("OK")
    ok_button.setDefault(True)
    ok_button.setMinimumWidth(90)
    ok_button.clicked.connect(dialog.accept)
    button_row.addWidget(ok_button)
    button_row.addStretch()
    layout.addLayout(button_row)

    dialog.setLayout(layout)
    dialog.setMinimumWidth(260)
    dialog.adjustSize()
    dialog.setFixedSize(dialog.sizeHint())
    dialog.exec_()


def resolve_output_path(self: Any, output_dir: str | Path | None) -> Path | None:
    """Validates and creates the output directory. Returns the Path on success, None on failure."""
    if not output_dir:
        QMessageBox.warning(self, "Error", "An output directory has not been selected.")
        return None
    try:
        output_path = Path(output_dir).expanduser()
    except (TypeError, ValueError) as e:
        QMessageBox.warning(self, "Error", f"Invalid output directory: {output_dir}\n{e}")
        return None
    if output_path.exists() and not output_path.is_dir():
        QMessageBox.warning(self, "Error", f"The specified output path is not a directory: {output_path}")
        return None
    if not output_path.exists():
        try:
            output_path.mkdir(parents=True, exist_ok=True)
            logger.info("Created output directory: %s", output_path)
        except Exception as e:
            logger.exception("Failed to create output directory: %s", output_path)
            QMessageBox.warning(self, "Error", f"Failed to create output directory: {output_path}\n{e}")
            return None
    try:
        with tempfile.NamedTemporaryFile(prefix=".ct_write_test_", dir=output_path, delete=True):
            pass
    except OSError as e:
        logger.exception("Output directory is not writable: %s", output_path)
        QMessageBox.warning(self, "Error", f"The selected output directory is not writable: {output_path}\n{e}")
        return None
    return output_path
