import os
from typing import Any

from pymol import cmd
from PyQt5.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

from functions.calculating.get_cmap import get_cmap
from functions.calculating.get_matrix import get_matrix

from functions.importing.retrieve_chain import retrieve_chain

from functions.plots.circuit_plot import circuit_plot
from functions.plots.matrix_plot import matrix_plot
from functions.plots.matrix_plot_model import matrix_plot_model

from functions.exporting.export_cmap3 import export_cmap3
from functions.exporting.export_mat import export_mat

from utils.non_polymer import has_non_polymer_atoms
from utils.folding_score import get_folding_score


def run_standard_analysis(self: Any) -> None:
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
            "The opened file contains non-polymer atoms, which can interfere with Circuit Topology. Please use the 'Remove Non-Polymer Atoms' button to remove them."
        )

    vals = self.get_values()
    selected_obj = self.dropdown_objects.currentText()
    if (selected_obj == "Select a file." or not selected_obj):
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

    chains = cmd.get_chains(selected_obj)
    file_name = f"{selected_obj}_export.pdb"
    cmd.save(file_name, selected_obj)
    single_dist = vals["cutoff_distance"]
    single_numcontacts = vals["cutoff_numcontacts"]
    single_neighbour = vals["exclude_neighbour"]
    base_file_typeless = selected_obj
    single_chain, protid = retrieve_chain(file_name)
    if os.path.exists(file_name):
        os.remove(os.path.abspath(file_name))
    output_directory = vals["output_directory"]

    if len(chains) > 1:
        level = "model"
        print("The supplied object has multiple chains. Performing multi-chain CT analysis...")
    else:
        level = "chain"

    idx, numbering, protid, _ = get_cmap(single_chain, level=level, cutoff_distance=single_dist,
                                                    cutoff_numcontacts=single_numcontacts,
                                                    exclude_neighbour=single_neighbour)
    if level == "chain":
        mat, psc, _ = get_matrix(idx, protid)
    else:
        mat, _, _ = get_matrix(idx, protid)
    # plots
    if circuit_plot_enabled:
        circuit_plot(index=idx, protid=protid, numbering=numbering)
    if matrix_plot_enabled:
        if level == "chain":
            matrix_plot(mat=mat, protid=protid)
        else:
            matrix_plot_model(mat=mat, protid=protid)

    if folding_score_enabled or export_cmap3_enabled:
        for c in chains:
            file_name = f"{selected_obj}_chain_{c}_export.pdb"

            cmd.save(file_name, f"{selected_obj} and chain {c}", state=cmd.get_state())
            folding_chain, p = retrieve_chain(file_name)
            i, n, p, _= get_cmap(folding_chain, cutoff_distance=single_dist,
                                            cutoff_numcontacts=single_numcontacts, exclude_neighbour=single_neighbour)
            m, psc, _ = get_matrix(i, p)

            if folding_score_enabled:
                # To handle incomplete chains
                if psc == [p, 0, 0, 0]:
                    print(f"Cannot create topology matrix for chain {c}, so folding score cannot be calculated!")
                    if os.path.exists(file_name):
                        os.remove(os.path.abspath(file_name))
                    continue

                print(f"Calculating folding score for chain {c} ...")
                folding_score = get_folding_score(m, i, n)

                if os.path.exists(file_name):
                    os.remove(os.path.abspath(file_name))

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
                file_base = os.path.basename(file_name)
                typeless_file_base = file_base.split('.')[0]
                print(f"Exporting contact map as .csv for chain {c} ...")
                export_cmap3(i, typeless_file_base, n, output_directory)
                if os.path.exists(file_name):
                    os.remove(os.path.abspath(file_name))

    if export_mat_enabled:
        export_mat(idx, mat, base_file_typeless, output_directory)
