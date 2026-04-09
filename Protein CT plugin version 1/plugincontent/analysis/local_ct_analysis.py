import os

from pymol import cmd
from pymol.Qt import QtWidgets

from ..functions.calculating.local_ct import local_ct
from ..functions.calculating.get_cmap import get_cmap
from ..functions.calculating.get_matrix import get_matrix

from ..functions.importing.retrieve_chain import retrieve_chain

from ..functions.plots.local_topology_plot import local_topology_plot

from ..functions.exporting.export_cmap3 import export_cmap3
from ..functions.exporting.export_mat import export_mat

from ..utils.non_polymer import has_non_polymer_atoms

def run_local_ct(self: QtWidgets.QWidget) -> None:
    """
    Runs the local circuit topology analysis.
    
    Args:
        self: The QtWidget object (CTDialog instance) calling this function.
    """
    # check for non-polymer atoms
    if has_non_polymer_atoms():
        QtWidgets.QMessageBox.warning(self, "Warning",
                                        "The opened file contains non-polymer atoms, which can interfere with Circuit Topology. Please use the 'Remove Non-Polymer Atoms' button to remove them.")

    vals = self.get_local_values()
    # Retrieve imported file as a selected object in PyMOL
    selected_obj = f"{self.local_dropdown_objects.currentText()} and chain {self.chain_combo_box.currentText()}"

    if (selected_obj == "Select a file." or not selected_obj):
        QtWidgets.QMessageBox.warning(self, "Error",
                                        "To use local Circuit Topology, please select the desired object from the dropdown menu first!")
        return

    local_ct_plot = vals["local_topology_plot"]
    residue_id = vals["res_id"] - self.box_res_id.minimum()
    contact = vals["contact_type"]
    local_ct_enabled = vals["local_ct"]
    export_cmap3_enabled = vals["export_cmap3"]
    export_mat_enabled = vals["export_mat"]

    # Check to see if GUI has at least one checkbox ticked for the 'run analysis' part
    if not local_ct_plot and not local_ct and not export_cmap3_enabled and not export_mat_enabled:
        QtWidgets.QMessageBox.warning(self, "Error", "No checkboxes for plotting or exporting have been ticked!")
        return

    file_name = f"{selected_obj}_export.pdb"
    cmd.save(file_name, selected_obj, state=cmd.get_state())
    local_dist = vals["cutoff_distance"]
    local_numcontacts = vals["cutoff_numcontacts"]
    local_neighbour = vals["exclude_neighbour"]
    base_file_typeless = file_name.split('.')[0]
    local_chain, protid = retrieve_chain(file_name)
    if os.path.exists(file_name):
        os.remove(os.path.abspath(file_name))

    idx, numbering, protid, res_names = get_cmap(local_chain, cutoff_distance=local_dist,
                                                    cutoff_numcontacts=local_numcontacts,
                                                    exclude_neighbour=local_neighbour)
    mat, psc = get_matrix(idx, protid)
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