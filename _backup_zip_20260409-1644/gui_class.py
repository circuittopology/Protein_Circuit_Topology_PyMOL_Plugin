from pymol import cmd  # pylint: disable=import-error, no-name-in-module
from typing import Optional

from pymol.Qt import QtWidgets, QtCore  # pylint: disable=import-error, no-name-in-module

from .utils.get_values import get_values, get_local_values, get_multiple_values, get_vis_vals
from .utils.clear_file import clear_selected_single_file, clear_selected_local_file
from .utils.directory import (
    choose_file,
    choose_local_file,
    choose_output_dir,
    choose_local_output_dir,
    choose_input_dir_multi,
    choose_output_dir_multi,
)

from .utils.object_change import handle_standard_object_change, handle_local_object_change
from .utils.non_polymer import show_warning_dialog
from .utils.residues import get_residue_range, update_residue_range
from .utils.helpers import update_chain_combo_box, init_timers, object_exists
from .utils.config import SECTION_STYLESHEET
from .utils.updates import update_list, update_local_list, update_output_widgets, update_output_widgets_local, update_output_widgets_multi
from .utils.trajectory import select_mol_file, select_xtc_file, export_frames_from_traj

from .analysis.local_ct_analysis import run_local_ct
from .analysis.single_file_analysis import run_standard_analysis
from .analysis.single_frame_analysis import run_single_frame_analysis, toggle_frame_controls
from .analysis.multiple_file_analysis import run_multi_analysis
from .analysis.visualization import visualize_molecule

from .tabs.local_tab import init_local_tab
from .tabs.single_file_tab import init_single_file_tab
from .tabs.multiple_file_tab import init_multi_file_tab

if not hasattr(cmd, "object_exists"):
    setattr(cmd, "object_exists", object_exists)

class CTDialog(QtWidgets.QDialog):
    """
    Main dialog class for the Circuit Topology tool.
    """

    # adding class methods from utils
    # get_values.py
    @QtCore.pyqtSlot()
    def get_values(self) -> None:
        """Retrieves and processes standard values."""
        return get_values(self)

    @QtCore.pyqtSlot()
    def get_local_values(self) -> None:
        """Retrieves and processes local values."""
        return get_local_values(self)
    
    @QtCore.pyqtSlot()
    def get_multiple_values(self) -> None:
        """Retrieves and processes multiple values."""
        return get_multiple_values(self)
    
    @QtCore.pyqtSlot()
    def get_vis_vals(self) -> None:
        """Retrieves visualization values."""
        return get_vis_vals(self)
    
    # clear_file.py
    @QtCore.pyqtSlot()
    def clear_selected_local_file(self) -> None:
        """Clears the currently selected local file."""
        clear_selected_local_file(self)

    @QtCore.pyqtSlot()
    def clear_selected_single_file(self) -> None:
        """Clears the currently selected single file."""
        clear_selected_single_file(self)

    # directory.py
    @QtCore.pyqtSlot()
    def choose_file(self) -> None:
        """Opens a dialog to choose a file."""
        choose_file(self)

    @QtCore.pyqtSlot()
    def choose_local_file(self) -> None:
        """Opens a dialog to choose a local file."""
        choose_local_file(self)

    @QtCore.pyqtSlot()
    def choose_output_dir(self) -> None:
        """Opens a dialog to choose an output directory."""
        choose_output_dir(self)

    @QtCore.pyqtSlot()
    def choose_local_output_dir(self) -> None:
        """Opens a dialog to choose a local output directory."""
        choose_local_output_dir(self)

    @QtCore.pyqtSlot()
    def choose_input_dir_multi(self) -> None:
        """Opens a dialog to choose a multiple input directory."""
        choose_input_dir_multi(self)
    
    @QtCore.pyqtSlot()
    def choose_output_dir_multi(self) -> None:
        """Opens a dialog to choose a multiple output directory."""
        choose_output_dir_multi(self)

    # object_change.py
    @QtCore.pyqtSlot()
    def handle_local_object_change(self, obj_name: Optional[str] = None) -> None:
        """Handles changes in the selected local object."""
        if obj_name is None:
            obj_name = self.local_dropdown_objects.currentText()
        handle_local_object_change(self, obj_name)

    @QtCore.pyqtSlot()
    def handle_standard_object_change(self, obj_name: Optional[str] = None) -> None:
        """Handles changes in the selected standard object."""
        if obj_name is None:
            obj_name = self.dropdown_objects.currentText()
        handle_standard_object_change(self, obj_name)

    # non_polymer.py
    @QtCore.pyqtSlot()
    def show_warning_dialog(self) -> None:
        """Shows a warning dialog for non-polymer selections."""
        show_warning_dialog(self)

    # residues.py
    @QtCore.pyqtSlot()
    def get_residue_range(self, obj_name: Optional[str] = None) -> None:
        """Gets the residue range for the selected object."""
        if obj_name is None:
            obj_name = self.local_dropdown_objets.currentText()
        get_residue_range(self, obj_name)

    @QtCore.pyqtSlot()
    def update_residue_range(self) -> None:
        """Updates the displayed residue range."""
        update_residue_range(self)

    # helpers.py
    @QtCore.pyqtSlot()
    def update_chain_combo_box(self) -> None:
        """Updates the chain combo box choices."""
        update_chain_combo_box(self)

    @QtCore.pyqtSlot()
    def init_timers(self) -> None:
        """Initializes application timers."""
        init_timers(self)

    # updates.py
    @QtCore.pyqtSlot()
    def update_list(self) -> None:
        """Updates the general list."""
        update_list(self)

    @QtCore.pyqtSlot()
    def update_local_list(self) -> None:
        """Updates the local list."""
        update_local_list(self)

    @QtCore.pyqtSlot()
    def update_output_widgets(self) -> None:
        """Updates general output widgets."""
        update_output_widgets(self)

    @QtCore.pyqtSlot()
    def update_output_widgets_local(self) -> None:
        """Updates local output widgets."""
        update_output_widgets_local(self)

    @QtCore.pyqtSlot()
    def update_output_widgets_multi(self) -> None:
        """Updates multi-file output widgets."""
        update_output_widgets_multi(self)
    
    # trajectory.py
    @QtCore.pyqtSlot()
    def select_mol_file(self) -> None:
        """Selects a molecule file."""
        select_mol_file(self)
    
    @QtCore.pyqtSlot()
    def select_xtc_file(self) -> None:
        """Selects an XTC trajectory file."""
        select_xtc_file(self)

    @QtCore.pyqtSlot()
    def export_frames_from_traj(self) -> None:
        """Exports frames from a trajectory."""
        export_frames_from_traj(self)

    # tabs
    @QtCore.pyqtSlot()
    def init_local_tab(self) -> None:
        """Initializes the local tab UI."""
        init_local_tab(self)

    @QtCore.pyqtSlot()
    def init_single_file_tab(self) -> None:
        """Initializes the single file tab UI."""
        init_single_file_tab(self)

    @QtCore.pyqtSlot()
    def init_multi_file_tab(self) -> None:
        """Initializes the multi-file tab UI."""
        init_multi_file_tab(self)

    # analysis functions
    @QtCore.pyqtSlot()
    def run_local_ct(self) -> None:
        """Runs the local circuit topology analysis."""
        run_local_ct(self)

    @QtCore.pyqtSlot()
    def run_standard_analysis(self) -> None:
        """Runs the standard circuit topology analysis."""
        run_standard_analysis(self)

    @QtCore.pyqtSlot()
    def run_single_frame_analysis(self) -> None:
        """Runs the single frame analysis."""
        run_single_frame_analysis(self)

    @QtCore.pyqtSlot()
    def run_multi_analysis(self) -> None:
        """Runs multiple file analysis."""
        run_multi_analysis(self)

    @QtCore.pyqtSlot()
    def visualize_molecule(self, contact_type: str) -> None:
        """Visualizes the molecule based on contact type."""
        visualize_molecule(self, contact_type)
    
    @QtCore.pyqtSlot(bool)
    def toggle_frame_controls(self, enabled: bool) -> None:
        """Toggles frame controls."""
        toggle_frame_controls(self, enabled=enabled)
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        """Initializes the CTDialog instance."""
        super().__init__(parent)

        self.current_objects: set[str] = set()
        self.current_local_objects: set[str] = set()

        self.setWindowTitle("Circuit Topology Tool")
        self.setGeometry(100, 100, 480, 540)
        self.setStyleSheet(SECTION_STYLESHEET)

        self.init_ui()
        self.init_timers()
    
    def init_ui(self) -> None:
        """Sets up the initial user interface elements."""
        self.tab_widget = QtWidgets.QTabWidget()

        self.local_tab = QtWidgets.QWidget()
        self.single_file_tab = QtWidgets.QWidget()
        self.multi_file_tab = QtWidgets.QWidget()

        self.tab_widget.addTab(self.local_tab, "Local Circuit Topology")
        self.tab_widget.addTab(self.single_file_tab, "Single‑File Analysis")
        self.tab_widget.addTab(self.multi_file_tab, "Multi‑File Analysis")

        self.init_local_tab()
        self.init_single_file_tab()
        self.init_multi_file_tab()

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)
