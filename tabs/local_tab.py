from typing import Any

from PyQt5.QtWidgets import (
    QVBoxLayout, QGroupBox, QHBoxLayout, QLabel, QPushButton, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QSizePolicy
)
from PyQt5.QtCore import Qt

from utils.helpers import make_info_button, make_param_row


def init_local_tab(self: Any) -> None:
    """
    Initializes the 'Local Circuit Topology' tab in the GUI.
    Sets up widgets for file selection, parameter input, analysis options, and exporting.

    Args:
        self: The main GUI class instance.
    """
    # Local tab's layout
    local_layout = QVBoxLayout(self.local_tab)

    # Visual grouper for the input file or select pymol object menu
    input_grp = QGroupBox("PyMOL object selection")
    input_lay = QVBoxLayout(input_grp)

    self.local_dir_button = QPushButton("Choose file ...")
    self.local_clear_file_btn = QPushButton("Clear selection")
    info_btn_local_clear = make_info_button("Clear the current file/object and unload it from PyMOL.")
    self.local_clear_file_btn.clicked.connect(self.clear_selected_local_file)

    self.local_dir_label = QLabel("No file selected...")
    self.local_dir_label.setWordWrap(True)
    self.local_dir_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    self.local_dir_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

    self.local_dir_button.clicked.connect(self.choose_local_file)

    btn_row = QHBoxLayout()
    btn_row.addWidget(self.local_dir_button)
    btn_row.addWidget(self.local_clear_file_btn)
    btn_row.addWidget(info_btn_local_clear)
    input_lay.addLayout(btn_row)
    input_lay.addWidget(self.local_dir_label)

    self.local_dropdown_objects = QComboBox()

    self.local_dropdown_objects.currentTextChanged.connect(self.handle_local_object_change)

    self.local_dropdown_objects.currentTextChanged.connect(
        lambda: self.get_residue_range(self.local_dropdown_objects.currentText()))
    input_lay.addWidget(QLabel("Loaded PyMOL objects:"))
    input_lay.addWidget(self.local_dropdown_objects)

    local_layout.addWidget(input_grp)

    # Visual group that groups all basic hyperparameters
    params_grp = QGroupBox("Contact map parameters")
    params_lay = QVBoxLayout(params_grp)

    # Distance cutoff
    self.cutoff_distance_local = QDoubleSpinBox()
    self.cutoff_distance_local.setRange(0.1, 20.0)
    self.cutoff_distance_local.setValue(4.5)
    self.cutoff_distance_local.setSingleStep(0.1)
    self.cutoff_distance_local.setToolTip("Distance cutoff in Ångströms")
    params_lay.addLayout(make_param_row(
        "Cutoff distance (Å):",
        "Set the distance threshold (in Å) for considering two residues as contacting. (Range: 0.1–20.0)",
        self.cutoff_distance_local))

    # Min contacts
    self.min_contacts_local = QSpinBox()
    self.min_contacts_local.setRange(5, 45)
    self.min_contacts_local.setValue(5)
    self.min_contacts_local.setToolTip("Minimum number of contacts (range: 5-45)")
    params_lay.addLayout(make_param_row(
        "Number of contacts:",
        "Minimum number of atomic contacts required to define a valid residue connection. (Range: 5-45)",
        self.min_contacts_local))

    # Exclude neighbours
    self.exclude_neighbor_local = QSpinBox()
    self.exclude_neighbor_local.setRange(1, 10)
    self.exclude_neighbor_local.setValue(3)
    params_lay.addLayout(make_param_row(
        "Exclude neighbours:",
        "Number of neighboring residues to exclude (range: 1-10)",
        self.exclude_neighbor_local))

    local_layout.addWidget(params_grp)

    analysis_grp = QGroupBox("Analysis options")
    analysis_lay = QVBoxLayout(analysis_grp)

    # Contact type
    self.dropdown_contact_type = QComboBox()
    self.dropdown_contact_type.addItems(["Series (S)", "Parallel (P)", "Inverse parallel (P‑)", "Cross (X)"])
    analysis_lay.addWidget(QLabel("Contact type:"))
    analysis_lay.addWidget(self.dropdown_contact_type)

    # Residue ID selection
    self.chain_combo_box = QComboBox()
    self.chain_combo_box.currentTextChanged.connect(self.update_residue_range)
    analysis_lay.addWidget(QLabel("Chain:"))
    analysis_lay.addWidget(self.chain_combo_box)
    self.box_res_id = QSpinBox()
    self.box_res_id.setRange(0, 300)
    self.box_res_id.setValue(0)
    analysis_lay.addWidget(QLabel("Residue ID:"))
    analysis_lay.addWidget(self.box_res_id)

    # Plotting and enabling local CT
    self.checkbox_local_ct = QCheckBox("Run local CT")
    self.checkbox_local_ct_plot = QCheckBox("Plot local CT")
    analysis_lay.addWidget(self.checkbox_local_ct)
    analysis_lay.addWidget(self.checkbox_local_ct_plot)

    local_layout.addWidget(analysis_grp)

    # Exporting
    export_grp = QGroupBox("Export")
    export_lay = QVBoxLayout(export_grp)

    self.checkbox_local_cmap3 = QCheckBox("Contact map (.csv)")
    self.checkbox_local_matrix = QCheckBox("Relations matrix (.csv)")
    export_lay.addWidget(self.checkbox_local_cmap3)
    export_lay.addWidget(self.checkbox_local_matrix)

    # Output directory selector
    self.output_local_button = QPushButton("Choose output directory …")
    self.output_local_label = QLabel("No output directory selected")
    self.output_local_label.setWordWrap(True)
    self.output_local_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    self.output_local_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
    self.output_local_txt = QLabel("Output directory:")

    self.output_local_button.clicked.connect(self.choose_local_output_dir)

    export_lay.addWidget(self.output_local_txt)
    export_lay.addWidget(self.output_local_button)
    export_lay.addWidget(self.output_local_label)

    self.output_local_txt.hide()
    self.output_local_button.hide()
    self.output_local_label.hide()

    # reveal/hide when boxes toggled
    for cb in (self.checkbox_local_matrix, self.checkbox_local_cmap3):
        cb.toggled.connect(self.update_output_widgets_local)

    local_layout.addWidget(export_grp)

    # Button for clearing nonprotein elements
    remove_row = QHBoxLayout()
    self.remove_non_polymer_button = QPushButton("Remove Non-Polymer Atoms")
    self.remove_non_polymer_button.clicked.connect(self.show_warning_dialog)
    info_button_local = make_info_button(
        "The Circuit Topology tool only processes protein atoms. If your loaded PyMOL object contains non-polymer atoms, the tool will not be able to handle them. Upon clicking this button, non-polymer atoms will be removed. Be aware that heteroatoms in CIF files can interfere with Circuit Topology.")
    remove_row.addWidget(self.remove_non_polymer_button)
    remove_row.addWidget(info_button_local)
    remove_row.addStretch()
    local_layout.addLayout(remove_row)

    # Run local analysis button
    self.local_run_button = QPushButton("Run local analysis")
    self.local_run_button.clicked.connect(self.run_local_ct)
    local_layout.addWidget(self.local_run_button)

    local_layout.addStretch()