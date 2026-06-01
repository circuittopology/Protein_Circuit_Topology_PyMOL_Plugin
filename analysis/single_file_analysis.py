import logging
from typing import Any

from pymol import cmd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLabel, QMessageBox, QPushButton, QVBoxLayout

from functions.calculating.get_cmap import get_cmap
from functions.calculating.get_matrix import get_matrix
from functions.exporting.export_cmap3 import export_cmap3
from functions.exporting.export_mat import export_mat
from functions.importing.retrieve_chain import retrieve_chain
from functions.plots.circuit_plot import circuit_plot
from functions.plots.matrix_plot import matrix_plot
from functions.plots.matrix_plot_model import matrix_plot_model
from utils.folding_score import get_folding_score
from utils.helpers import resolve_output_path, temp_pdb_export
from utils.non_polymer import has_non_polymer_atoms
from utils.validation import (
    chain_selection,
    get_object_chains,
    object_exists,
    object_selection,
    selection_has_atoms,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def run_standard_analysis(self: Any) -> None:  # noqa: PLR0911, PLR0912, PLR0915
    """
    Runs the standard single-file circuit topology analysis.
    Handles data retrieval, calculation, plotting, and exporting.

    Args:
        self: The main GUI class instance.
    """
    # check for non-polymer atoms
    if has_non_polymer_atoms():
        QMessageBox.warning(
            self, "Warning",
            "The opened file contains non-polymer atoms, which can interfere with Circuit Topology. Please use the 'Remove Non-Polymer Atoms' button to remove them.",
        )

    vals = self.get_values()
    selected_obj = self.dropdown_objects.currentText()
    if not object_exists(selected_obj):
        QMessageBox.warning(self, "Error", "To process your object with Circuit Topology, please select it from the dropdown menu!")
        return
    # Retrieving checkbox values
    folding_score_enabled = vals["folding_score"]
    circuit_plot_enabled = vals["circuit_plot"]
    matrix_plot_enabled = vals["matrix_plot"]
    export_cmap3_enabled = vals["export_cmap3"]
    export_mat_enabled = vals["export_mat"]

    # Check to see if GUI has at least one checkbox ticked for the 'run analysis' part
    if not circuit_plot_enabled and not matrix_plot_enabled and not export_cmap3_enabled and not export_mat_enabled and not folding_score_enabled:
        QMessageBox.warning(self, "Error", "No checkboxes for plots, CT folding score or exporting have been ticked.")
        return

    output_directory = vals["output_directory"]
    output_path = None
    if export_cmap3_enabled or export_mat_enabled:
        output_path = resolve_output_path(self, output_directory)
        if output_path is None:
            return

    chains = get_object_chains(selected_obj)
    if not chains:
        QMessageBox.warning(self, "Error", f"No protein chains were found for object: {selected_obj}")
        return
    if not selection_has_atoms(object_selection(selected_obj)):
        QMessageBox.warning(self, "Error", f"The selected object has no atoms to analyze: {selected_obj}")
        return

    try:
        with temp_pdb_export(object_selection(selected_obj)) as tmp_path:
            single_chain, protid = retrieve_chain(tmp_path)
    except Exception as e:
        logger.exception("Failed to export or parse selected object: %s", selected_obj)
        QMessageBox.warning(self, "Error", f"Failed to prepare the selected object for analysis:\n{e}")
        return

    single_dist = vals["cutoff_distance"]
    single_numcontacts = vals["cutoff_numcontacts"]
    single_neighbour = vals["exclude_neighbour"]
    base_file_typeless = selected_obj

    if len(chains) > 1:
        level = "model"
        logger.info("The supplied object has multiple chains. Performing multi-chain CT analysis...")
    else:
        level = "chain"

    try:
        idx, numbering, protid, _ = get_cmap(
            single_chain,
            level=level,
            cutoff_distance=single_dist,
            cutoff_numcontacts=single_numcontacts,
            exclude_neighbour=single_neighbour,
        )
        if idx.size == 0:
            QMessageBox.warning(self, "Warning", "No residue contacts were found with the current parameters.")
            return
        if level == "chain":
            mat, psc, _ = get_matrix(idx, protid)
        else:
            mat, _, _ = get_matrix(idx, protid)
    except Exception as e:
        logger.exception("Single-file analysis failed for %s", selected_obj)
        QMessageBox.warning(self, "Error", f"Analysis failed for {selected_obj}:\n{e}")
        return

    # plots
    try:
        if matrix_plot_enabled:
            if level == "chain":
                matrix_plot(mat=mat, protid=protid)
            else:
                matrix_plot_model(mat=mat, protid=protid)
        if circuit_plot_enabled:
            circuit_plot(index=idx, protid=protid, numbering=numbering)
    except Exception as e:
        logger.exception("Plotting failed for %s", selected_obj)
        QMessageBox.warning(self, "Error", f"Plotting failed for {selected_obj}:\n{e}")
        return

    cmap3_exports = []
    if folding_score_enabled or export_cmap3_enabled:
        for c in chains:
            current_selection = chain_selection(selected_obj, c)
            if not selection_has_atoms(current_selection):
                logger.warning("Skipping empty chain selection: %s", current_selection)
                continue
            try:
                with temp_pdb_export(current_selection, state=cmd.get_state()) as tmp_path:
                    folding_chain, p = retrieve_chain(tmp_path)
                i, n, p, _= get_cmap(
                    folding_chain,
                    cutoff_distance=single_dist,
                    cutoff_numcontacts=single_numcontacts,
                    exclude_neighbour=single_neighbour,
                )
                if i.size == 0:
                    logger.warning("No contacts found for chain %s; skipping chain-level work", c)
                    continue
                m, psc, _ = get_matrix(i, p)

                if folding_score_enabled:
                    # To handle incomplete chains
                    if psc == [p, 0, 0, 0]:
                        logger.warning("Cannot create topology matrix for chain %s, so folding score cannot be calculated!", c)
                        continue

                    logger.info("Calculating folding score for chain %s ...", c)
                    folding_score = get_folding_score(m, i, n)

                    # Show the score in a pop-up tab (QDialog)
                    dialog = QDialog(self)
                    dialog.setWindowTitle("CT Folding Score")
                    layout = QVBoxLayout()

                    label = QLabel(f"CT Folding Score: {folding_score}")
                    label.setAlignment(Qt.AlignCenter)
                    layout.addWidget(label)

                    ok_button = QPushButton("OK")
                    ok_button.clicked.connect(dialog.accept)
                    layout.addWidget(ok_button)

                    dialog.setLayout(layout)
                    dialog.setFixedSize(200, 100)
                    dialog.exec_()

                if export_cmap3_enabled:
                    cmap3_exports.append((i, f"{selected_obj}_chain_{c}", n))
            except Exception as e:
                logger.exception("Failed processing chain %s", c)
                QMessageBox.warning(self, "Error", f"Failed processing chain {c}:\n{e}")
                return

    if export_cmap3_enabled or export_mat_enabled:
        if output_path is None:
            return
        try:
            for i, chain_label, n in cmap3_exports:
                logger.info("Exporting contact map as .csv for chain %s ...", chain_label)
                export_cmap3(i, chain_label, n, output_path)
            if export_mat_enabled:
                export_mat(idx, mat, base_file_typeless, output_path)
        except Exception as e:
            logger.exception("Export failed for %s", selected_obj)
            QMessageBox.warning(self, "Error", f"Export failed for {selected_obj}:\n{e}")
