import sys
from pathlib import Path
from pymol.Qt import QtWidgets, QtCore
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
# pylint: disable=wrong-import-position
from utils.helpers import make_info_button

def init_single_file_tab(self):
    t1_layout = QtWidgets.QVBoxLayout(self.single_file_tab)

    # Visual grouper for importing files/objects into the GUI for single-file analysis
    input_grp = QtWidgets.QGroupBox("PyMOL object selection")
    input_lay = QtWidgets.QVBoxLayout(input_grp)

    self.dir_button = QtWidgets.QPushButton("Choose file …")
    self.clear_file_button = QtWidgets.QPushButton("Clear selection")
    info_btn_single_clear = make_info_button("Clear the current file/object and unload it from PyMOL.")
    self.clear_file_button.setToolTip("Clear the current file/object and unload it from PyMOL.")
    self.clear_file_button.clicked.connect(self.clear_selected_single_file)
    self.dir_label = QtWidgets.QLabel("No file selected")
    self.dir_label.setWordWrap(True)
    self.dir_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
    self.dir_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

    self.dir_button.clicked.connect(self.choose_file)
    btnrow = QtWidgets.QHBoxLayout()
    btnrow.addWidget(self.dir_button)
    btnrow.addWidget(self.clear_file_button)
    btnrow.addWidget(info_btn_single_clear)
    input_lay.addLayout(btnrow)
    input_lay.addWidget(self.dir_label)

    self.dropdown_objects = QtWidgets.QComboBox()

    self.dropdown_objects.currentTextChanged.connect(self.handle_standard_object_change)

    input_lay.addWidget(QtWidgets.QLabel("Loaded PyMOL objects:"))
    input_lay.addWidget(self.dropdown_objects)

    t1_layout.addWidget(input_grp)

    # Hyperparameters that can be adjusted
    params_grp = QtWidgets.QGroupBox("Contact map parameters")
    params_lay = QtWidgets.QVBoxLayout(params_grp)

    # Cutoff distance
    self.cutoff_distance_spin = QtWidgets.QDoubleSpinBox()
    self.cutoff_distance_spin.setRange(0.1, 20.0)
    self.cutoff_distance_spin.setValue(4.5)
    self.cutoff_distance_spin.setSingleStep(0.1)

    dist_row = QtWidgets.QHBoxLayout()
    dist_row.addWidget(QtWidgets.QLabel("Cutoff distance (Å):"))
    dist_row.addWidget(make_info_button(
        "Set the distance threshold (in Å) for considering two residues as contacting. (Range: 0.1–20.0)"))
    dist_row.addStretch()
    dist_row.addWidget(self.cutoff_distance_spin)
    params_lay.addLayout(dist_row)

    # Minimum number of contacts
    self.min_contacts_spin = QtWidgets.QSpinBox()
    self.min_contacts_spin.setRange(5, 45)
    self.min_contacts_spin.setValue(5)

    mc_row = QtWidgets.QHBoxLayout()
    mc_row.addWidget(QtWidgets.QLabel("Number of contacts:"))
    mc_row.addWidget(make_info_button(
        "Minimum number of atomic contacts required to define a valid residue connection. (Range: 5-45)"))
    mc_row.addStretch()
    mc_row.addWidget(self.min_contacts_spin)
    params_lay.addLayout(mc_row)

    # Exclude neighbours
    self.exclude_neighbor_spin = QtWidgets.QSpinBox()
    self.exclude_neighbor_spin.setRange(1, 10)
    self.exclude_neighbor_spin.setValue(3)

    ex_row = QtWidgets.QHBoxLayout()
    ex_row.addWidget(QtWidgets.QLabel("Exclude neighbours:"))
    ex_row.addWidget(make_info_button("Number of neighboring residues to exclude (range: 1-10)"))
    ex_row.addStretch()
    ex_row.addWidget(self.exclude_neighbor_spin)
    params_lay.addLayout(ex_row)

    t1_layout.addWidget(params_grp)

    # Plotting options for single-file analysis
    plot_grp = QtWidgets.QGroupBox("Plot")
    plot_lay = QtWidgets.QVBoxLayout(plot_grp)

    self.checkbox_matrix_plot = QtWidgets.QCheckBox("Matrix plot")
    self.checkbox_circuit_plot = QtWidgets.QCheckBox("Circuit plot")

    for w in (self.checkbox_matrix_plot, self.checkbox_circuit_plot):
        plot_lay.addWidget(w)

    t1_layout.addWidget(plot_grp)

    # Visualization layout with 3 nice buttons
    vis_grp = QtWidgets.QGroupBox("Visualize Circuit Topology by contact type")
    vis_lay = QtWidgets.QVBoxLayout(vis_grp)

    # Button for series contacts
    self.S_button = QtWidgets.QPushButton("Series (S)")
    self.S_button.clicked.connect(lambda: self.visualize_molecule(contact_type="S"))

    # Button for parallel contacts
    self.P_button = QtWidgets.QPushButton("Parallel (P)")
    self.P_button.clicked.connect(lambda: self.visualize_molecule(contact_type="P"))

    # Button for cross contacts
    self.X_button = QtWidgets.QPushButton("Cross (X)")
    self.X_button.clicked.connect(lambda: self.visualize_molecule(contact_type="X"))

    for b in (self.S_button, self.P_button, self.X_button):
        vis_lay.addWidget(b)

    t1_layout.addWidget(vis_grp)

    # Exporting
    export_grp = QtWidgets.QGroupBox("Export")
    export_lay = QtWidgets.QVBoxLayout(export_grp)

    self.checkbox_export_cmap3 = QtWidgets.QCheckBox("Contact map (.csv)")
    self.checkbox_export_matrix = QtWidgets.QCheckBox("Relations matrix (.csv)")
    export_lay.addWidget(self.checkbox_export_cmap3)
    export_lay.addWidget(self.checkbox_export_matrix)

    # Output directory selector (hidden until one of the check‑boxes is ticked)
    self.output_dir_button = QtWidgets.QPushButton("Choose output directory …")
    self.output_dir_label = QtWidgets.QLabel("No output directory selected")
    self.output_dir_label.setWordWrap(True)
    self.output_dir_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
    self.output_dir_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
    self.output_txt = QtWidgets.QLabel("Output directory:")

    self.output_dir_button.clicked.connect(self.choose_output_dir)

    export_lay.addWidget(self.output_txt)
    export_lay.addWidget(self.output_dir_button)
    export_lay.addWidget(self.output_dir_label)

    self.output_txt.hide()
    self.output_dir_button.hide()
    self.output_dir_label.hide()

    self.checkbox_export_cmap3.toggled.connect(self.update_output_widgets)
    self.checkbox_export_matrix.toggled.connect(self.update_output_widgets)

    t1_layout.addWidget(export_grp)

    fold_grp = QtWidgets.QGroupBox("CT Folding Score calculator")
    fold_lay = QtWidgets.QVBoxLayout(fold_grp)

    # Small adjustment to folding score ordering
    self.checkbox_folding_score = QtWidgets.QCheckBox("Enable Folding Score")
    fold_lay_adj = QtWidgets.QHBoxLayout()
    fold_lay_adj.addWidget(make_info_button(
        "Quantifies how well a protein’s structure is compact and stable based on its contact patterns"))
    fold_lay_adj.addStretch()
    fold_lay_adj.addWidget(self.checkbox_folding_score)
    fold_lay.addLayout(fold_lay_adj)
    t1_layout.addWidget(fold_grp)

    # Button for clearing nonprotein elements
    remove_row_tab1 = QtWidgets.QHBoxLayout()
    self.remove_non_polymer_button_tab1 = QtWidgets.QPushButton("Remove Non-Polymer Atoms")
    self.remove_non_polymer_button_tab1.clicked.connect(self.show_warning_dialog)
    info_button_tab1 = make_info_button(
        "The Circuit Topology tool only processes protein atoms. If your loaded PyMOL object contains non-polymer atoms, the tool will not be able to handle them. Upon clicking this button, non-polymer atoms will be removed. Be aware that heteroatoms in CIF files can interfere with Circuit Topology.")
    remove_row_tab1.addWidget(self.remove_non_polymer_button_tab1)
    remove_row_tab1.addWidget(info_button_tab1)
    remove_row_tab1.addStretch()
    t1_layout.addLayout(remove_row_tab1)

    self.run_button = QtWidgets.QPushButton("Run analysis")
    self.run_button.clicked.connect(self.run_standard_analysis)
    t1_layout.addWidget(self.run_button)

    t1_layout.addStretch()