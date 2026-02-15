import sys
from pathlib import Path
from typing import Any
from pymol.Qt import QtWidgets, QtCore
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
# pylint: disable=wrong-import-position
from utils.helpers import make_info_button

def init_multi_file_tab(self: Any) -> None:
    """
    Initializes the 'Multi-File Analysis' tab in the GUI.
    Sets up widgets for directory selection, trajectory handling,
    parameter input, analysis options, and exporting.

    Args:
        self: The main GUI class instance.
    """
    scroll_area = QtWidgets.QScrollArea(self.multi_file_tab)
    scroll_area.setWidgetResizable(True)

    scroll_widget = QtWidgets.QWidget()
    scroll_widget.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
    scroll_area.setWidgetResizable(True)
    scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)

    dir_grp = QtWidgets.QGroupBox("Directory")
    dir_lay = QtWidgets.QVBoxLayout(dir_grp)
    self.input_dir_button_multi = QtWidgets.QPushButton("Choose input directory …")
    self.input_dir_button_multi.clicked.connect(self.choose_input_dir_multi)
    self.input_dir_label_multi = QtWidgets.QLabel("No input directory selected")
    self.input_dir_label_multi.setWordWrap(True)
    self.input_dir_label_multi.setSizePolicy(
        QtWidgets.QSizePolicy.Expanding,
        QtWidgets.QSizePolicy.Preferred
    )
    self.input_dir_label_multi.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
    dir_lay.addWidget(self.input_dir_button_multi)
    dir_lay.addWidget(self.input_dir_label_multi)
    scroll_layout.addWidget(dir_grp)

    traj_grp = QtWidgets.QGroupBox("Import a trajectory and PDB")
    traj_lay = QtWidgets.QVBoxLayout(traj_grp)

    self.traj_mol_button = QtWidgets.QPushButton("Select a .PDB file …")
    self.traj_mol_button.clicked.connect(self.select_mol_file)
    self.traj_mol_label = QtWidgets.QLabel("No PDB file selected")

    self.traj_xtc_button = QtWidgets.QPushButton("Select trajectory file (.xtc) …")
    self.traj_xtc_button.clicked.connect(self.select_xtc_file)
    self.traj_xtc_label = QtWidgets.QLabel("No trajectory file selected")

    self.export_frames_button = QtWidgets.QPushButton("Convert to multiple PDBs")
    self.export_frames_button.clicked.connect(self.export_frames_from_traj)

    self.traj_status_label = QtWidgets.QLabel("")
    traj_lay.addWidget(self.traj_mol_button)
    traj_lay.addWidget(self.traj_mol_label)
    traj_lay.addWidget(self.traj_xtc_button)
    traj_lay.addWidget(self.traj_xtc_label)
    traj_lay.addWidget(self.export_frames_button)
    traj_lay.addWidget(self.traj_status_label)

    scroll_layout.addWidget(traj_grp)

    params_grp = QtWidgets.QGroupBox("Contact-map parameters")
    params_lay = QtWidgets.QVBoxLayout(params_grp)

    self.cutoff_distance_multi = QtWidgets.QDoubleSpinBox()
    self.cutoff_distance_multi.setRange(0.1, 20.0)
    self.cutoff_distance_multi.setValue(4.5)
    self.cutoff_distance_multi.setSingleStep(0.1)
    cutoff_row = QtWidgets.QHBoxLayout()
    cutoff_row.addWidget(QtWidgets.QLabel("Cut-off distance (Å):"))
    cutoff_row.addWidget(
        make_info_button("Distance threshold (Å) for two residues to be considered in contact."))
    cutoff_row.addStretch()
    cutoff_row.addWidget(self.cutoff_distance_multi)
    params_lay.addLayout(cutoff_row)

    self.min_contacts_multi = QtWidgets.QSpinBox()
    self.min_contacts_multi.setRange(5, 45)
    self.min_contacts_multi.setValue(5)
    mc_row = QtWidgets.QHBoxLayout()
    mc_row.addWidget(QtWidgets.QLabel("Minimum contacts:"))
    mc_row.addWidget(
        make_info_button(
            "Minimum atomic contacts required to define a valid connection."
            )
    )
    mc_row.addStretch()
    mc_row.addWidget(self.min_contacts_multi)
    params_lay.addLayout(mc_row)

    self.exclude_neighbor_multi = QtWidgets.QSpinBox()
    self.exclude_neighbor_multi.setRange(1, 10)
    self.exclude_neighbor_multi.setValue(3)
    ex_row = QtWidgets.QHBoxLayout()
    ex_row.addWidget(QtWidgets.QLabel("Exclude neighbours:"))
    ex_row.addWidget(make_info_button("Number of neighbouring residues to ignore."))
    ex_row.addStretch()
    ex_row.addWidget(self.exclude_neighbor_multi)
    params_lay.addLayout(ex_row)

    scroll_layout.addWidget(params_grp)

    self.checkbox_single_frame_analysis = QtWidgets.QCheckBox(
        "Enable per-frame trajectory analysis"
    )
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
    self.frame_selector_layout = QtWidgets.QHBoxLayout()
    self.frame_selector_label = QtWidgets.QLabel("Select trajectory frame:")
    self.frame_selector_spinbox = QtWidgets.QSpinBox()
    self.frame_selector_spinbox.setMinimum(1)  # Will be updated dynamically
    self.frame_selector_spinbox.setEnabled(False)
    self.frame_selector_layout.addWidget(self.frame_selector_label)
    self.frame_selector_layout.addWidget(self.frame_selector_spinbox)
    self.frame_selector_layout.addStretch()
    scroll_layout.addLayout(self.frame_selector_layout)

    # Run single-frame analysis button (initially hidden)
    self.run_single_frame_button = QtWidgets.QPushButton("Analyze selected trajectory frame")
    self.run_single_frame_button.setEnabled(False)
    self.run_single_frame_button.clicked.connect(self.run_single_frame_analysis)
    scroll_layout.addWidget(self.run_single_frame_button)

    filters_grp = QtWidgets.QGroupBox("Optional filters")
    filters_lay = QtWidgets.QVBoxLayout(filters_grp)

    # Fixed 'Distance:' label appearing
    self.checkbox_length_filtering = QtWidgets.QCheckBox("Enable length filtering")
    self.filtering_distance_label = QtWidgets.QLabel("Distance:")
    self.filtering_distance_spin = QtWidgets.QSpinBox()
    self.filtering_distance_spin.setRange(0, 1000)
    self.filtering_distance_spin.setValue(0)
    self.dropdown_length_filter_mode = QtWidgets.QComboBox()
    self.dropdown_length_filter_mode.addItems(["equality (=)", "less than (<)", "greater than (>)"])
    self.filtering_distance_label.hide()
    self.filtering_distance_spin.hide()
    self.dropdown_length_filter_mode.hide()
    length_row = QtWidgets.QHBoxLayout()
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
    distance_row = QtWidgets.QHBoxLayout()
    distance_row.addWidget(self.filtering_distance_label)
    distance_row.addWidget(self.filtering_distance_spin)
    distance_row.addWidget(self.dropdown_length_filter_mode)
    distance_row.addStretch()
    filters_lay.addLayout(distance_row)

    self.checkbox_energy_filtering = QtWidgets.QCheckBox("Enable energy filtering")
    self.dropdown_energy_mode = QtWidgets.QComboBox()
    self.dropdown_energy_mode.addItems(["Attractive / stabilising (+)", "Repulsive / destabilising (−)"])
    self.dropdown_energy_mode.hide()
    energy_row = QtWidgets.QHBoxLayout()
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

    plot_grp = QtWidgets.QGroupBox("Plots")
    plot_lay = QtWidgets.QVBoxLayout(plot_grp)
    self.checkbox_matrix_multi = QtWidgets.QCheckBox("Matrix plot")
    self.checkbox_circuit_multi = QtWidgets.QCheckBox("Circuit plot")
    self.checkbox_stats_multi = QtWidgets.QCheckBox("Statistics plot")
    for cb in (self.checkbox_matrix_multi, self.checkbox_circuit_multi, self.checkbox_stats_multi):
        plot_lay.addWidget(cb)
    scroll_layout.addWidget(plot_grp)

    export_grp = QtWidgets.QGroupBox("Export")
    export_lay = QtWidgets.QVBoxLayout(export_grp)
    self.checkbox_export_cmap3_multi = QtWidgets.QCheckBox("Contact map (.csv)")
    self.checkbox_export_matrix_multi = QtWidgets.QCheckBox("Relations matrix (.csv)")
    self.checkbox_export_psc_multi = QtWidgets.QCheckBox("P,S,X list (.csv)")
    self.checkbox_export_psc_multi.setToolTip(
        "Counts the number of Parallel (P), Series (S), and Cross (X) contacts per residue in each file. P,S,X list only applies to multiple-file analysis. For per-frame analysis, ticking this option will have no effect.")
    for cb in (self.checkbox_export_cmap3_multi, self.checkbox_export_matrix_multi, self.checkbox_export_psc_multi):
        export_lay.addWidget(cb)
    self.checkbox_plot_psc = QtWidgets.QCheckBox("P,S,X contacts plotted over time")
    self.checkbox_plot_psc.setToolTip("Informative only for protein trajectories")
    self.checkbox_plot_psc.setEnabled(False)
    self.checkbox_export_psc_multi.toggled.connect(self.checkbox_plot_psc.setEnabled)
    export_lay.addWidget(self.checkbox_plot_psc)
    self.output_txt_multi = QtWidgets.QLabel("Output directory:")
    self.output_dir_button_multi = QtWidgets.QPushButton("Choose output directory …")
    self.output_dir_label_multi = QtWidgets.QLabel("No output directory selected")
    self.output_dir_label_multi.setWordWrap(True)
    self.output_dir_label_multi.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
    self.output_dir_label_multi.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
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

    self.run_multi_button = QtWidgets.QPushButton("Run multi-file CT analysis")
    self.run_multi_button.clicked.connect(self.run_multi_analysis)
    scroll_layout.addWidget(self.run_multi_button)
    scroll_layout.addStretch()

    self.checkbox_length_filtering.toggled.connect(self.filtering_distance_spin.setVisible)
    self.checkbox_length_filtering.toggled.connect(self.dropdown_length_filter_mode.setVisible)
    self.checkbox_energy_filtering.toggled.connect(self.dropdown_energy_mode.setVisible)

    scroll_area.setWidget(scroll_widget)
    layout = QtWidgets.QVBoxLayout(self.multi_file_tab)
    layout.addWidget(scroll_area)
