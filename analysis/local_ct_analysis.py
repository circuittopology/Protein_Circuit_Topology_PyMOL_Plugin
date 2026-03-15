import os
import sys
from pathlib import Path
from typing import Any

from pymol import cmd
from PyQt5.QtWidgets import QMessageBox

from functions.calculating.local_ct import local_ct
from functions.calculating.get_cmap import get_cmap
from functions.calculating.get_matrix import get_matrix

from functions.importing.retrieve_chain import retrieve_chain

from functions.plots.local_topology_plot import local_topology_plot

from functions.exporting.export_cmap3 import export_cmap3
from functions.exporting.export_mat import export_mat

from utils.non_polymer import has_non_polymer_atoms
from utils.config import WARN_MSG, LOCAL_CT_WARN, CHECKBOX_WARN

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

def run_local_ct(self: Any) -> None:
    """
    Runs the local circuit topology analysis based on user-selected parameters.
    Handles data retrieval, calculation, plotting, and exporting.

    Args:
        self: The main GUI class instance.
    """
    # check for non-polymer atoms
    if has_non_polymer_atoms():
        QMessageBox.warning(self, "Warning", WARN_MSG)

    vals = self.get_local_values()
    # Retrieve imported file as a selected object in PyMOL
    curr_local_obj = self.local_dropdown_objects.currentText()
    curr_chain = self.chain_combo_box.currentText()
    selected_obj = f"{curr_local_obj} and chain {curr_chain}"

    if (selected_obj == "Select a file." or not selected_obj):
        QMessageBox.warning(self, "Error", LOCAL_CT_WARN)
        return

    local_ct_plot = vals["local_topology_plot"]
    residue_id = vals["res_id"] - self.box_res_id.minimum()
    contact = vals["contact_type"]
    local_ct_enabled = vals["local_ct"]
    export_cmap3_enabled = vals["export_cmap3"]
    export_mat_enabled = vals["export_mat"]

    # Check to see if GUI has at least one checkbox ticked for the 'run analysis' part
    if not (local_ct_plot or local_ct_enabled or export_cmap3_enabled or export_mat_enabled):
        QMessageBox.warning(self, "Error", CHECKBOX_WARN)
        return

    file_name = f"{selected_obj}_export.pdb"
    cmd.save(file_name, selected_obj, state=cmd.get_state())
    local_dist = vals["cutoff_distance"]
    local_numcontacts = vals["cutoff_numcontacts"]
    local_neighbour = vals["exclude_neighbour"]
    base_file_typeless = file_name.split('.', maxsplit=1)[0]
    local_chain, protid = retrieve_chain(file_name)
    if os.path.exists(file_name):
        os.remove(os.path.abspath(file_name))

    idx, numbering, protid, _ = get_cmap(
        chain=local_chain,
        cutoff_distance=local_dist,
        cutoff_numcontacts=local_numcontacts,
        exclude_neighbour=local_neighbour
    )

    mat, _ = get_matrix(idx, protid)
    if local_ct_plot:
        local_topology_plot(idx, mat, numbering, protid, residue_id, contact)
    if local_ct_enabled:
        print(local_ct(idx, mat, numbering))

    output_directory = vals["output_directory"]
    # exported csv
    if export_cmap3_enabled:
        export_cmap3(idx, base_file_typeless, numbering, output_directory)
    if export_mat_enabled:
        export_mat(idx, mat, base_file_typeless, output_directory)
