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

from utils.helpers import make_info_button, make_param_row


def _build_local_input_group(self: Any) -> QGroupBox:
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

    return input_grp


def _build_local_params_group(self: Any) -> QGroupBox:
    params_grp = QGroupBox("Contact map parameters")
    params_lay = QVBoxLayout(params_grp)

    self.cutoff_distance_local = QDoubleSpinBox()
    self.cutoff_distance_local.setRange(0.1, 20.0)
    self.cutoff_distance_local.setValue(4.5)
    self.cutoff_distance_local.setSingleStep(0.1)
    self.cutoff_distance_local.setToolTip("Distance cutoff in Ångströms")
    params_lay.addLayout(make_param_row(
        "Cutoff distance (Å):",
        "Set the distance threshold (in Å) for considering two residues as contacting. (Range: 0.1 – 20.0)",  # noqa: RUF001
        self.cutoff_distance_local))

    self.min_contacts_local = QSpinBox()
    self.min_contacts_local.setRange(5, 45)
    self.min_contacts_local.setValue(5)
    self.min_contacts_local.setToolTip("Minimum number of contacts (range: 5 - 45)")
    params_lay.addLayout(make_param_row(
        "Number of contacts:",
        "Minimum number of atomic contacts required to define a valid residue connection. (Range: 5 - 45)",
        self.min_contacts_local))

    self.exclude_neighbor_local = QSpinBox()
    self.exclude_neighbor_local.setRange(1, 10)
    self.exclude_neighbor_local.setValue(3)
    params_lay.addLayout(make_param_row(
        "Exclude neighbours:",
        "Number of neighboring residues to exclude (range: 1 - 10)",
        self.exclude_neighbor_local))

    return params_grp


def _build_local_analysis_group(self: Any) -> QGroupBox:
    analysis_grp = QGroupBox("Analysis options")
    analysis_lay = QVBoxLayout(analysis_grp)

    self.dropdown_contact_type = QComboBox()
    self.dropdown_contact_type.addItems(["Series (S)", "Parallel (P)", "Inverse parallel (IP)", "Cross (X)"])
    analysis_lay.addWidget(QLabel("Contact type:"))
    analysis_lay.addWidget(self.dropdown_contact_type)

    self.chain_combo_box = QComboBox()
    self.chain_combo_box.currentTextChanged.connect(self.update_residue_range)
    analysis_lay.addWidget(QLabel("Chain:"))
    analysis_lay.addWidget(self.chain_combo_box)
    self.box_res_id = QSpinBox()
    self.box_res_id.setRange(0, 300)
    self.box_res_id.setValue(0)
    analysis_lay.addWidget(QLabel("Residue ID:"))
    analysis_lay.addWidget(self.box_res_id)

    self.checkbox_local_ct = QCheckBox("Run local CT")
    self.checkbox_local_ct_plot = QCheckBox("Plot local CT")
    analysis_lay.addWidget(self.checkbox_local_ct)
    analysis_lay.addWidget(self.checkbox_local_ct_plot)

    return analysis_grp


def _build_local_export_group(self: Any) -> QGroupBox:
    export_grp = QGroupBox("Export")
    export_lay = QVBoxLayout(export_grp)

    self.checkbox_local_cmap3 = QCheckBox("Contact map (.csv)")
    self.checkbox_local_matrix = QCheckBox("Relations matrix (.csv)")
    export_lay.addWidget(self.checkbox_local_cmap3)
    export_lay.addWidget(self.checkbox_local_matrix)

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

    for cb in (self.checkbox_local_matrix, self.checkbox_local_cmap3):
        cb.toggled.connect(self.update_output_widgets_local)

    return export_grp


def init_local_tab(self: Any) -> None:
    """
    Initializes the 'Local Circuit Topology' tab in the GUI.
    Sets up widgets for file selection, parameter input, analysis options, and exporting.

    Args:
        self: The main GUI class instance.
    """
    local_layout = QVBoxLayout(self.local_tab)

    local_layout.addWidget(_build_local_input_group(self))
    local_layout.addWidget(_build_local_params_group(self))
    local_layout.addWidget(_build_local_analysis_group(self))
    local_layout.addWidget(_build_local_export_group(self))

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

    self.local_run_button = QPushButton("Run local analysis")
    self.local_run_button.clicked.connect(self.run_local_ct)
    local_layout.addWidget(self.local_run_button)

    local_layout.addStretch()
