from typing import Any

from PyQt5.QtWidgets import (
    QScrollArea, QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QSizePolicy
)
from PyQt5.QtCore import Qt

from utils.helpers import make_info_button


def init_multi_file_tab(self: Any) -> None:
    """
    Initializes the 'Multi-File Analysis' tab in the GUI.
    Sets up widgets for directory selection, trajectory handling,
    parameter input, analysis options, and exporting.

    Args:
        self: The main GUI class instance.
    """
    scroll_area = QScrollArea(self.multi_file_tab)
    scroll_area.setWidgetResizable(True)

    scroll_widget = QWidget()
    scroll_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
    scroll_area.setWidgetResizable(True)
    scroll_layout = QVBoxLayout(scroll_widget)

    dir_grp = QGroupBox("Directory")
    dir_lay = QVBoxLayout(dir_grp)
    self.input_dir_button_multi = QPushButton("Choose input directory …")
    self.input_dir_button_multi.clicked.connect(self.choose_input_dir_multi)
    self.input_dir_label_multi = QLabel("No input directory selected")
    self.input_dir_label_multi.setWordWrap(True)
    self.input_dir_label_multi.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    self.input_dir_label_multi.setTextInteractionFlags(Qt.TextSelectableByMouse)
    dir_lay.addWidget(self.input_dir_button_multi)
    dir_lay.addWidget(self.input_dir_label_multi)
    scroll_layout.addWidget(dir_grp)

    traj_grp = QGroupBox("Import a trajectory and PDB")
    traj_lay = QVBoxLayout(traj_grp)

    self.traj_mol_button = QPushButton("Select a .PDB file …")
    self.traj_mol_button.clicked.connect(self.select_mol_file)
    self.traj_mol_label = QLabel("No PDB file selected")

    self.traj_xtc_button = QPushButton("Select trajectory file (.xtc) …")
    self.traj_xtc_button.clicked.connect(self.select_xtc_file)
    self.traj_xtc_label = QLabel("No trajectory file selected")

    self.export_frames_button = QPushButton("Convert to multiple PDBs")
    self.export_frames_button.clicked.connect(self.export_frames_from_traj)

    self.traj_status_label = QLabel("")
    traj_lay.addWidget(self.traj_mol_button)
    traj_lay.addWidget(self.traj_mol_label)
    traj_lay.addWidget(self.traj_xtc_button)
    traj_lay.addWidget(self.traj_xtc_label)
    traj_lay.addWidget(self.export_frames_button)
    traj_lay.addWidget(self.traj_status_label)

    scroll_layout.addWidget(traj_grp)

    params_grp = QGroupBox("Contact-map parameters")
    params_lay = QVBoxLayout(params_grp)

    self.cutoff_distance_multi = QDoubleSpinBox()
    self.cutoff_distance_multi.setRange(0.1, 20.0)
    self.cutoff_distance_multi.setValue(4.5)
    self.cutoff_distance_multi.setSingleStep(0.1)
    cutoff_row = QHBoxLayout()
    cutoff_row.addWidget(QLabel("Cut-off distance (Å):"))
    cutoff_row.addWidget(make_info_button("Distance threshold (Å) for two residues to be considered in contact."))
    cutoff_row.addStretch()
    cutoff_row.addWidget(self.cutoff_distance_multi)
    params_lay.addLayout(cutoff_row)

    self.min_contacts_multi = QSpinBox()
    self.min_contacts_multi.setRange(5, 45)
    self.min_contacts_multi.setValue(5)
    mc_row = QHBoxLayout()
    mc_row.addWidget(QLabel("Minimum contacts:"))
    mc_row.addWidget(make_info_button("Minimum atomic contacts required to define a valid connection."))
    mc_row.addStretch()
    mc_row.addWidget(self.min_contacts_multi)
    params_lay.addLayout(mc_row)

    self.exclude_neighbor_multi = QSpinBox()
    self.exclude_neighbor_multi.setRange(1, 10)
    self.exclude_neighbor_multi.setValue(3)
    ex_row = QHBoxLayout()
    ex_row.addWidget(QLabel("Exclude neighbours:"))
    ex_row.addWidget(make_info_button("Number of neighbouring residues to ignore."))
    ex_row.addStretch()
    ex_row.addWidget(self.exclude_neighbor_multi)
    params_lay.addLayout(ex_row)

    scroll_layout.addWidget(params_grp)

    self.checkbox_single_frame_analysis = QCheckBox("Enable per-frame trajectory analysis")
    self.checkbox_single_frame_analysis.setToolTip(
        """Per-frame trajectory analysis should only be used when processing trajectories
        (not multiple files). It is also possible to select the imported trajectory PDB object
        from the dropdown menu in single-file analysis and use PyMOL's built-in controls to
        sift through individual frames and analyse them."""
    )
    self.checkbox_single_frame_analysis.setChecked(False)
    self.checkbox_single_frame_analysis.toggled.connect(self.toggle_frame_controls)
    scroll_layout.addWidget(self.checkbox_single_frame_analysis)

    # Frame selector (initially hidden)
    self.frame_selector_layout = QHBoxLayout()
    self.frame_selector_label = QLabel("Select trajectory frame:")
    self.frame_selector_spinbox = QSpinBox()
    self.frame_selector_spinbox.setMinimum(1)  # Will be updated dynamically
    self.frame_selector_spinbox.setEnabled(False)
    self.frame_selector_layout.addWidget(self.frame_selector_label)
    self.frame_selector_layout.addWidget(self.frame_selector_spinbox)
    self.frame_selector_layout.addStretch()
    scroll_layout.addLayout(self.frame_selector_layout)

    # Run single-frame analysis button (initially hidden)
    self.run_single_frame_button = QPushButton("Analyze selected trajectory frame")
    self.run_single_frame_button.setEnabled(False)
    self.run_single_frame_button.clicked.connect(self.run_single_frame_analysis)
    scroll_layout.addWidget(self.run_single_frame_button)

    filters_grp = QGroupBox("Optional filters")
    filters_lay = QVBoxLayout(filters_grp)

    # Fixed 'Distance:' label appearing
    self.checkbox_length_filtering = QCheckBox("Enable length filtering")
    self.filtering_distance_label = QLabel("Distance:")
    self.filtering_distance_spin = QSpinBox()
    self.filtering_distance_spin.setRange(0, 1000)
    self.filtering_distance_spin.setValue(0)
    self.dropdown_length_filter_mode = QComboBox()
    self.dropdown_length_filter_mode.addItems(["equality (=)", "less than (<)", "greater than (>)"])
    self.filtering_distance_label.hide()
    self.filtering_distance_spin.hide()
    self.dropdown_length_filter_mode.hide()
    length_row = QHBoxLayout()
    length_row.addWidget(self.checkbox_length_filtering)
    length_row.addWidget(make_info_button(
        """Filter contacts by sequence distance.
        Length filtering only applies to multiple-file analysis.
        For per-frame analysis, ticking this option will have no effect.
        NOTE:
        1) MANIPULATING LENGTH FILTERING CAN RETURN EMPTY CONTACT MAPS.
        2) THE CURRENT CIRCUIT TOPOLOGY ANALYSIS TOOL DOES NOT SUPPORT LENGTH FILTERING FOR MULTI-CHAIN PROTEINS.
        THE ANALYSIS WILL SKIP LENGTH FILTERING STEP FOR MULTI-CHAIN PROTEINS."""
    ))
    length_row.addStretch()
    filters_lay.addLayout(length_row)
    distance_row = QHBoxLayout()
    distance_row.addWidget(self.filtering_distance_label)
    distance_row.addWidget(self.filtering_distance_spin)
    distance_row.addWidget(self.dropdown_length_filter_mode)
    distance_row.addStretch()
    filters_lay.addLayout(distance_row)

    self.checkbox_energy_filtering = QCheckBox("Enable energy filtering")
    self.dropdown_energy_mode = QComboBox()
    self.dropdown_energy_mode.addItems(["Attractive / stabilising (+)", "Repulsive / destabilising (−)"])
    self.dropdown_energy_mode.hide()
    energy_row = QHBoxLayout()
    energy_row.addWidget(self.checkbox_energy_filtering)
    energy_row.addWidget(make_info_button(
        """Keep only attractive or only repulsive interactions.
        Energy filtering only applies to multiple-file analysis.
        For per-frame analysis, ticking this option will have no effect.
        NOTE:
        THE CURRENT CIRCUIT TOPOLOGY ANALYSIS TOOL DOES NOT SUPPORT ENERGY FILTERING
        FOR MULTI-CHAIN PROTEINS. THE ANALYSIS WILL SKIP ENERGY FILTERING STEP
        FOR MULTI-CHAIN PROTEINS."""
    ))
    energy_row.addStretch()
    filters_lay.addLayout(energy_row)
    filters_lay.addWidget(self.dropdown_energy_mode)

    scroll_layout.addWidget(filters_grp)

    plot_grp = QGroupBox("Plots")
    plot_lay = QVBoxLayout(plot_grp)
    self.checkbox_matrix_multi = QCheckBox("Matrix plot")
    self.checkbox_circuit_multi = QCheckBox("Circuit plot")
    self.checkbox_stats_multi = QCheckBox("Statistics plot")
    for cb in (self.checkbox_matrix_multi, self.checkbox_circuit_multi, self.checkbox_stats_multi):
        plot_lay.addWidget(cb)
    scroll_layout.addWidget(plot_grp)

    export_grp = QGroupBox("Export")
    export_lay = QVBoxLayout(export_grp)
    self.checkbox_export_cmap3_multi = QCheckBox("Contact map (.csv)")
    self.checkbox_export_matrix_multi = QCheckBox("Relations matrix (.csv)")
    self.checkbox_export_psc_multi = QCheckBox("P,S,X list (.csv)")
    self.checkbox_export_psc_multi.setToolTip(
        "Counts the number of Parallel (P), Series (S), and Cross (X) contacts per residue in each file. P,S,X list only applies to multiple-file analysis. For per-frame analysis, ticking this option will have no effect.")
    for cb in (self.checkbox_export_cmap3_multi, self.checkbox_export_matrix_multi, self.checkbox_export_psc_multi):
        export_lay.addWidget(cb)
    self.checkbox_plot_psc = QCheckBox("P,S,X contacts plotted over time")
    self.checkbox_plot_psc.setToolTip("Informative only for protein trajectories")
    self.checkbox_plot_psc.setEnabled(False)
    self.checkbox_export_psc_multi.toggled.connect(self.checkbox_plot_psc.setEnabled)
    export_lay.addWidget(self.checkbox_plot_psc)
    self.output_txt_multi = QLabel("Output directory:")
    self.output_dir_button_multi = QPushButton("Choose output directory …")
    self.output_dir_label_multi = QLabel("No output directory selected")
    self.output_dir_label_multi.setWordWrap(True)
    self.output_dir_label_multi.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    self.output_dir_label_multi.setTextInteractionFlags(Qt.TextSelectableByMouse)
    self.output_txt_multi.hide()
    self.output_dir_button_multi.hide()
    self.output_dir_label_multi.hide()
    self.output_dir_button_multi.clicked.connect(self.choose_output_dir_multi)

    export_lay.addWidget(self.output_txt_multi)
    export_lay.addWidget(self.output_dir_button_multi)
    export_lay.addWidget(self.output_dir_label_multi)

    for cb in (self.checkbox_export_cmap3_multi, self.checkbox_export_matrix_multi, self.checkbox_export_psc_multi):
        cb.toggled.connect(self.update_output_widgets_multi)

    scroll_layout.addWidget(export_grp)

    self.run_multi_button = QPushButton("Run multi-file CT analysis")
    self.run_multi_button.clicked.connect(self.run_multi_analysis)
    scroll_layout.addWidget(self.run_multi_button)
    scroll_layout.addStretch()

    self.checkbox_length_filtering.toggled.connect(self.filtering_distance_spin.setVisible)
    self.checkbox_length_filtering.toggled.connect(self.dropdown_length_filter_mode.setVisible)
    self.checkbox_energy_filtering.toggled.connect(self.dropdown_energy_mode.setVisible)

    scroll_area.setWidget(scroll_widget)
    layout = QVBoxLayout(self.multi_file_tab)
    layout.addWidget(scroll_area)
