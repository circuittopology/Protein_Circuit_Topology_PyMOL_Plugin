from pathlib import Path
import sys
from typing import Any, Dict
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
# pylint: disable=wrong-import-position

from utils.config import CONTACT_MAP

def get_vis_vals(self: Any) -> Dict[str, Any]:
    """
    Retrieves visualization parameters from the GUI.

    Args:
        self: The main GUI class instance.

    Returns:
        dict: A dictionary containing visualization parameters.
    """
    return {
        "cutoff_distance": self.cutoff_distance_spin.value(),
        "cutoff_numcontacts": self.min_contacts_spin.value(),
        "exclude_neighbour": self.exclude_neighbor_spin.value(),
    }

def get_values(self: Any) -> Dict[str, Any]:
    """
    Retrieves parameters for single-file analysis from the GUI.

    Args:
        self: The main GUI class instance.

    Returns:
        dict: A dictionary containing analysis parameters.
    """
    return {
        "output_directory": getattr(self, "selected_output_dir", None),
        "cutoff_distance": self.cutoff_distance_spin.value(),
        "cutoff_numcontacts": self.min_contacts_spin.value(),
        "exclude_neighbour": self.exclude_neighbor_spin.value(),
        "circuit_plot": self.checkbox_circuit_plot.isChecked(),
        "folding_score": self.checkbox_folding_score.isChecked(),
        "matrix_plot": self.checkbox_matrix_plot.isChecked(),
        "export_cmap3": self.checkbox_export_cmap3.isChecked(),
        "export_mat": self.checkbox_export_matrix.isChecked()
    }

def get_local_values(self: Any) -> Dict[str, Any]:
    """
    Retrieves parameters for local analysis from the GUI.

    Args:
        self: The main GUI class instance.

    Returns:
        dict: A dictionary containing local analysis parameters.
    """
    contact_type = CONTACT_MAP.get(self.dropdown_contact_type.currentText(), "X")
    return {
        "output_directory": getattr(self, "selected_output_dir_local", None),
        "cutoff_distance": self.cutoff_distance_local.value(),
        "cutoff_numcontacts": self.min_contacts_local.value(),
        "exclude_neighbour": self.exclude_neighbor_local.value(),
        "local_topology_plot": self.checkbox_local_ct_plot.isChecked(),
        "res_id": self.box_res_id.value(),
        "contact_type": contact_type,
        "local_ct": self.checkbox_local_ct.isChecked(),
        "export_cmap3": self.checkbox_local_cmap3.isChecked(),
        "export_mat": self.checkbox_local_matrix.isChecked()
    }

def get_multiple_values(self: Any) -> Dict[str, Any]:
    """
    Retrieves parameters for multi-file analysis from the GUI.

    Args:
        self: The main GUI class instance.

    Returns:
        dict: A dictionary containing multi-file analysis parameters.
    """
    len_filtering = self.checkbox_length_filtering.isChecked()
    energy_filtering = self.checkbox_energy_filtering.isChecked()
    len_dropdown = self.dropdown_length_filter_mode.currentText()
    energy_dropdown = self.dropdown_energy_mode.currentText()
    return {
        "directory": getattr(self, "selected_input_dir_multi", None),
        "traj_directory": getattr(self, "selected_traj_dir_multi", None),
        "output_directory": getattr(self, "selected_output_dir_multi", None),
        "cutoff_distance": self.cutoff_distance_multi.value(),
        "cutoff_numcontacts": self.min_contacts_multi.value(),
        "exclude_neighbour": self.exclude_neighbor_multi.value(),
        "circuit_plot": self.checkbox_circuit_multi.isChecked(),
        "matrix_plot": self.checkbox_matrix_multi.isChecked(),
        "stats_plot": self.checkbox_stats_multi.isChecked(),
        "export_cmap3": self.checkbox_export_cmap3_multi.isChecked(),
        "export_mat": self.checkbox_export_matrix_multi.isChecked(),
        "export_psc": self.checkbox_export_psc_multi.isChecked(),
        "plot_psc": self.checkbox_plot_psc.isChecked(),
        "length_filtering": len_filtering,
        "filtering_distance": self.filtering_distance_spin.value() if len_filtering else None,
        "length_filter_mode": len_dropdown if len_filtering else None,
        "energy_filtering": energy_filtering,
        "energy_filtering_mode": '-' if energy_dropdown == "Repulsive/Destabilizing (-)" else '+'
    }
