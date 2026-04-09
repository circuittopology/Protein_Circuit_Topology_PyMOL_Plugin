from pymol.Qt import QtWidgets, QtCore
from ..utils.helpers import make_info_button

def init_local_tab(self: QtWidgets.QWidget) -> None:
    """
    Initializes the local tab interface.
    
    Args:
        self: The QtWidget object.
    """
    # Local tab's layout
    local_layout = QtWidgets.QVBoxLayout(self.local_tab)

    # Visual grouper for the input file or select pymol object menu
    input_grp = QtWidgets.QGroupBox("PyMOL object selection")
    input_lay = QtWidgets.QVBoxLayout(input_grp)

    self.local_dir_button = QtWidgets.QPushButton("Choose file ...")
    self.local_clear_file_btn = QtWidgets.QPushButton("Clear selection")
    info_btn_local_clear = make_info_button("Clear the current file/object and unload it from PyMOL.")
    self.local_clear_file_btn.clicked.connect(self.clear_selected_local_file)

    self.local_dir_label = QtWidgets.QLabel("No file selected...")
    self.local_dir_label.setWordWrap(True)
    self.local_dir_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
    self.local_dir_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

    self.local_dir_button.clicked.connect(self.choose_local_file)

    btn_row = QtWidgets.QHBoxLayout()
    btn_row.addWidget(self.local_dir_button)
    btn_row.addWidget(self.local_clear_file_btn)
    btn_row.addWidget(info_btn_local_clear)
    input_lay.addLayout(btn_row)
    input_lay.addWidget(self.local_dir_label)

    self.local_dropdown_objects = QtWidgets.QComboBox()

    self.local_dropdown_objects.currentTextChanged.connect(self.handle_local_object_change)

    self.local_dropdown_objects.currentTextChanged.connect(
        lambda: self.get_residue_range(self.local_dropdown_objects.currentText()))
    input_lay.addWidget(QtWidgets.QLabel("Loaded PyMOL objects:"))
    input_lay.addWidget(self.local_dropdown_objects)

    local_layout.addWidget(input_grp)

    # Visual group that groups all basic hyperparameters
    params_grp = QtWidgets.QGroupBox("Contact map parameters")
    params_lay = QtWidgets.QVBoxLayout(params_grp)

    # Distance cutoff
    self.cutoff_distance_local = QtWidgets.QDoubleSpinBox()
    self.cutoff_distance_local.setRange(0.1, 20.0)
    self.cutoff_distance_local.setValue(4.5)
    self.cutoff_distance_local.setSingleStep(0.1)
    self.cutoff_distance_local.setToolTip("Distance cutoff in Ångströms")

    dist_row = QtWidgets.QHBoxLayout()
    dist_row.addWidget(QtWidgets.QLabel("Cutoff distance (Å):"))
    dist_row.addWidget(make_info_button(
        "Set the distance threshold (in Å) for considering two residues as contacting. (Range: 0.1–20.0)"))
    dist_row.addStretch()
    dist_row.addWidget(self.cutoff_distance_local)
    params_lay.addLayout(dist_row)

    # Min contacts
    self.min_contacts_local = QtWidgets.QSpinBox()
    self.min_contacts_local.setRange(5, 45)
    self.min_contacts_local.setValue(5)
    self.min_contacts_local.setToolTip("Minimum number of contacts (range: 5-45)")

    mc_row = QtWidgets.QHBoxLayout()
    mc_row.addWidget(QtWidgets.QLabel("Number of contacts:"))
    mc_row.addWidget(make_info_button(
        "Minimum number of atomic contacts required to define a valid residue connection. (Range: 5-45)"))
    mc_row.addStretch()
    mc_row.addWidget(self.min_contacts_local)
    params_lay.addLayout(mc_row)

    # Exclude neighbours
    self.exclude_neighbor_local = QtWidgets.QSpinBox()
    self.exclude_neighbor_local.setRange(1, 10)
    self.exclude_neighbor_local.setValue(3)

    ex_row = QtWidgets.QHBoxLayout()
    ex_row.addWidget(QtWidgets.QLabel("Exclude neighbours:"))
    ex_row.addWidget(make_info_button("Number of neighboring residues to exclude (range: 1-10)"))
    ex_row.addStretch()
    ex_row.addWidget(self.exclude_neighbor_local)
    params_lay.addLayout(ex_row)

    local_layout.addWidget(params_grp)

    analysis_grp = QtWidgets.QGroupBox("Analysis options")
    analysis_lay = QtWidgets.QVBoxLayout(analysis_grp)

    # Contact type
    self.dropdown_contact_type = QtWidgets.QComboBox()
    self.dropdown_contact_type.addItems(["Series (S)", "Parallel (P)", "Inverse parallel (P‑)", "Cross (X)"])
    analysis_lay.addWidget(QtWidgets.QLabel("Contact type:"))
    analysis_lay.addWidget(self.dropdown_contact_type)

    # Residue ID selection
    self.chain_combo_box = QtWidgets.QComboBox()
    self.chain_combo_box.currentTextChanged.connect(self.update_residue_range)
    analysis_lay.addWidget(QtWidgets.QLabel("Chain:"))
    analysis_lay.addWidget(self.chain_combo_box)
    self.box_res_id = QtWidgets.QSpinBox()
    self.box_res_id.setRange(0, 300)
    self.box_res_id.setValue(0)
    analysis_lay.addWidget(QtWidgets.QLabel("Residue ID:"))
    analysis_lay.addWidget(self.box_res_id)

    # Plotting and enabling local CT
    self.checkbox_local_ct = QtWidgets.QCheckBox("Run local CT")
    self.checkbox_local_ct_plot = QtWidgets.QCheckBox("Plot local CT")
    analysis_lay.addWidget(self.checkbox_local_ct)
    analysis_lay.addWidget(self.checkbox_local_ct_plot)

    local_layout.addWidget(analysis_grp)

    # Exporting
    export_grp = QtWidgets.QGroupBox("Export")
    export_lay = QtWidgets.QVBoxLayout(export_grp)

    self.checkbox_local_cmap3 = QtWidgets.QCheckBox("Contact map (.csv)")
    self.checkbox_local_matrix = QtWidgets.QCheckBox("Relations matrix (.csv)")
    export_lay.addWidget(self.checkbox_local_cmap3)
    export_lay.addWidget(self.checkbox_local_matrix)

    # Output directory selector
    self.output_local_button = QtWidgets.QPushButton("Choose output directory …")
    self.output_local_label = QtWidgets.QLabel("No output directory selected")
    self.output_local_label.setWordWrap(True)
    self.output_local_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
    self.output_local_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
    self.output_local_txt = QtWidgets.QLabel("Output directory:")

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
    remove_row = QtWidgets.QHBoxLayout()
    self.remove_non_polymer_button = QtWidgets.QPushButton("Remove Non-Polymer Atoms")
    self.remove_non_polymer_button.clicked.connect(self.show_warning_dialog)
    info_button_local = make_info_button(
        "The Circuit Topology tool only processes protein atoms. If your loaded PyMOL object contains non-polymer atoms, the tool will not be able to handle them. Upon clicking this button, non-polymer atoms will be removed. Be aware that heteroatoms in CIF files can interfere with Circuit Topology.")
    remove_row.addWidget(self.remove_non_polymer_button)
    remove_row.addWidget(info_button_local)
    remove_row.addStretch()
    local_layout.addLayout(remove_row)

    # Run local analysis button
    self.local_run_button = QtWidgets.QPushButton("Run local analysis")
    self.local_run_button.clicked.connect(self.run_local_ct)
    local_layout.addWidget(self.local_run_button)

    local_layout.addStretch()