from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
)

from utils.config import TRAJECTORY_COLOR_INFO
from utils.helpers import make_info_button, make_param_row


def _build_input_group(self: Any) -> QGroupBox:
    input_grp = QGroupBox("PyMOL object selection")
    input_lay = QVBoxLayout(input_grp)

    self.dir_button = QPushButton("Choose file …")
    self.clear_file_button = QPushButton("Clear selection")
    info_btn_single_clear = make_info_button("Clear the current file/object and unload it from PyMOL.")
    self.clear_file_button.setToolTip("Clear the current file/object and unload it from PyMOL.")
    self.clear_file_button.clicked.connect(self.clear_selected_single_file)
    self.dir_label = QLabel("No file selected")
    self.dir_label.setWordWrap(True)
    self.dir_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    self.dir_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

    self.dir_button.clicked.connect(self.choose_file)
    btnrow = QHBoxLayout()
    btnrow.addWidget(self.dir_button)
    btnrow.addWidget(self.clear_file_button)
    btnrow.addWidget(info_btn_single_clear)
    input_lay.addLayout(btnrow)
    input_lay.addWidget(self.dir_label)

    self.dropdown_objects = QComboBox()
    self.dropdown_objects.currentTextChanged.connect(self.handle_standard_object_change)
    input_lay.addWidget(QLabel("Loaded PyMOL objects:"))
    input_lay.addWidget(self.dropdown_objects)

    return input_grp


def _build_params_group(self: Any) -> QGroupBox:
    params_grp = QGroupBox("Contact map parameters")
    params_lay = QVBoxLayout(params_grp)

    self.cutoff_distance_spin = QDoubleSpinBox()
    self.cutoff_distance_spin.setRange(0.1, 20.0)
    self.cutoff_distance_spin.setValue(4.5)
    self.cutoff_distance_spin.setSingleStep(0.1)
    params_lay.addLayout(make_param_row(
        "Cutoff distance (Å):",
        """Set the distance threshold (in Å) for considering two residues as contacting.
        (Range: 0.1 - 20.0)""",
        self.cutoff_distance_spin))

    self.min_contacts_spin = QSpinBox()
    self.min_contacts_spin.setRange(5, 45)
    self.min_contacts_spin.setValue(5)
    params_lay.addLayout(make_param_row(
        "Number of contacts:",
        """Minimum number of atomic contacts required to define a valid residue connection.
        (Range: 5 - 45)""",
        self.min_contacts_spin))

    self.exclude_neighbor_spin = QSpinBox()
    self.exclude_neighbor_spin.setRange(1, 10)
    self.exclude_neighbor_spin.setValue(3)
    params_lay.addLayout(make_param_row(
        "Exclude neighbours:",
        "Number of neighboring residues to exclude (range: 1 - 10)",
        self.exclude_neighbor_spin))

    return params_grp


def _build_plot_group(self: Any) -> QGroupBox:
    plot_grp = QGroupBox("Plot")
    plot_lay = QVBoxLayout(plot_grp)

    self.checkbox_matrix_plot = QCheckBox("Matrix plot")
    self.checkbox_circuit_plot = QCheckBox("Circuit plot")

    for w in (self.checkbox_matrix_plot, self.checkbox_circuit_plot):
        plot_lay.addWidget(w)

    return plot_grp


def _build_vis_group(self: Any) -> QGroupBox:
    vis_grp = QGroupBox("Visualize Circuit Topology by contact type")
    vis_lay = QVBoxLayout(vis_grp)

    info_row = QHBoxLayout()
    info_row.addWidget(QLabel("Trajectory support"))
    info_row.addWidget(make_info_button(TRAJECTORY_COLOR_INFO))
    info_row.addStretch()
    vis_lay.addLayout(info_row)

    self.S_button = QPushButton("Series (S)")
    self.S_button.clicked.connect(lambda: self.visualize_molecule(contact_type="S"))

    self.P_button = QPushButton("Parallel (P)")
    self.P_button.clicked.connect(lambda: self.visualize_molecule(contact_type="P"))

    self.X_button = QPushButton("Cross (X)")
    self.X_button.clicked.connect(lambda: self.visualize_molecule(contact_type="X"))

    for b in (self.S_button, self.P_button, self.X_button):
        vis_lay.addWidget(b)

    return vis_grp


def _build_export_group(self: Any) -> QGroupBox:
    export_grp = QGroupBox("Export")
    export_lay = QVBoxLayout(export_grp)

    self.checkbox_export_cmap3 = QCheckBox("Contact map (.csv)")
    self.checkbox_export_matrix = QCheckBox("Relations matrix (.csv)")
    export_lay.addWidget(self.checkbox_export_cmap3)
    export_lay.addWidget(self.checkbox_export_matrix)

    self.output_dir_button = QPushButton("Choose output directory …")
    self.output_dir_label = QLabel("No output directory selected")
    self.output_dir_label.setWordWrap(True)
    self.output_dir_label.setSizePolicy(
        QSizePolicy.Expanding,
        QSizePolicy.Preferred,
    )
    self.output_dir_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
    self.output_txt = QLabel("Output directory:")

    self.output_dir_button.clicked.connect(self.choose_output_dir)

    export_lay.addWidget(self.output_txt)
    export_lay.addWidget(self.output_dir_button)
    export_lay.addWidget(self.output_dir_label)

    self.output_txt.hide()
    self.output_dir_button.hide()
    self.output_dir_label.hide()

    self.checkbox_export_cmap3.toggled.connect(self.update_output_widgets)
    self.checkbox_export_matrix.toggled.connect(self.update_output_widgets)

    return export_grp


def _build_folding_group(self: Any) -> QGroupBox:
    fold_grp = QGroupBox("CT Folding Score calculator")
    fold_lay = QVBoxLayout(fold_grp)

    self.checkbox_folding_score = QCheckBox("Enable Folding Score")
    fold_lay_adj = QHBoxLayout()
    fold_lay_adj.addWidget(make_info_button(
        """Quantifies how well a protein structure is compact and stable
        based on its contact patterns""",
    ))
    fold_lay_adj.addStretch()
    fold_lay_adj.addWidget(self.checkbox_folding_score)
    fold_lay.addLayout(fold_lay_adj)

    return fold_grp


def init_single_file_tab(self: Any) -> None:
    """
    Initializes the 'Single-File Analysis' tab in the GUI.
    Sets up widgets for file selection, parameter input, analysis options,
    visualization, and exporting.

    Args:
        self: The main GUI class instance.
    """
    t1_layout = QVBoxLayout(self.single_file_tab)

    t1_layout.addWidget(_build_input_group(self))
    t1_layout.addWidget(_build_params_group(self))
    t1_layout.addWidget(_build_plot_group(self))
    t1_layout.addWidget(_build_vis_group(self))
    t1_layout.addWidget(_build_export_group(self))
    t1_layout.addWidget(_build_folding_group(self))

    # Button for clearing nonprotein elements
    remove_row_tab1 = QHBoxLayout()
    self.remove_non_polymer_button_tab1 = QPushButton("Remove Non-Polymer Atoms")
    self.remove_non_polymer_button_tab1.clicked.connect(self.show_warning_dialog)
    info_button_tab1 = make_info_button(
        """The Circuit Topology tool only processes protein atoms.
        If your loaded PyMOL object contains non-polymer atoms, the tool will not be able to
        handle them. Upon clicking this button, non-polymer atoms will be removed.
        Be aware that heteroatoms in CIF files can interfere with Circuit Topology.""",
        )
    remove_row_tab1.addWidget(self.remove_non_polymer_button_tab1)
    remove_row_tab1.addWidget(info_button_tab1)
    remove_row_tab1.addStretch()
    t1_layout.addLayout(remove_row_tab1)

    self.run_button = QPushButton("Run analysis")
    self.run_button.clicked.connect(self.run_standard_analysis)
    t1_layout.addWidget(self.run_button)

    t1_layout.addStretch()
