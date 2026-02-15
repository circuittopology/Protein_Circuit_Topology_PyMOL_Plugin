def get_vis_vals(self):
    return {
        "cutoff_distance": self.cutoff_distance_spin.value(),
        "cutoff_numcontacts": self.min_contacts_spin.value(),
        "exclude_neighbour": self.exclude_neighbor_spin.value(),
    }

def get_values(self):
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

def get_local_values(self):
    return {
        "output_directory": getattr(self, "selected_output_dir_local", None),
        "cutoff_distance": self.cutoff_distance_local.value(),
        "cutoff_numcontacts": self.min_contacts_local.value(),
        "exclude_neighbour": self.exclude_neighbor_local.value(),
        "local_topology_plot": self.checkbox_local_ct_plot.isChecked(),
        "res_id": self.box_res_id.value(),
        "contact_type": 'S' if self.dropdown_contact_type.currentText() == "Series (S)" else 'P' if self.dropdown_contact_type.currentText() == "Parallel (P)" else 'IP' if self.dropdown_contact_type.currentText() == "Inverse parallel (P-)" else 'X',
        "local_ct": self.checkbox_local_ct.isChecked(),
        "export_cmap3": self.checkbox_local_cmap3.isChecked(),
        "export_mat": self.checkbox_local_matrix.isChecked()
    }

def get_multiple_values(self):
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
        "length_filtering": self.checkbox_length_filtering.isChecked(),
        "filtering_distance": self.filtering_distance_spin.value() if self.checkbox_length_filtering.isChecked() else None,
        "length_filter_mode": self.dropdown_length_filter_mode.currentText() if self.checkbox_length_filtering.isChecked() else None,
        "energy_filtering": self.checkbox_energy_filtering.isChecked(),
        "energy_filtering_mode": '-' if self.dropdown_energy_mode.currentText() == "Repulsive/Destabilizing (-)" else '+'
    }