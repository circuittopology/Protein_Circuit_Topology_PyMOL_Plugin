"""
GUI class and bindings for the Circuit Topology PyMOL plugin.

This module exposes the CTDialog class that encapsulates the Qt-based GUI used
to drive the plugin. The design follows a thin-wrapper pattern where GUI
slots delegate behavior to functions implemented in modular helper and analysis
submodules. This keeps the dialog class focused on UI wiring and lifecycle
management while business logic lives in reusable utilities.

Key responsibilities:
- Provide a persistent dialog instance that can be shown by the plugin entrypoint.
- Expose Qt slots that delegate to functions defined in the plugin's utilities.
- Manage UI initialization, timers and basic dialog state.
"""
import sys
from pathlib import Path
from typing import Optional
from pymol import cmd  # pylint: disable=import-error, no-name-in-module
from pymol.Qt import QtWidgets, QtCore  # pylint: disable=import-error, no-name-in-module

PROJECT_ROOT = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(PROJECT_ROOT))
# pylint: disable=wrong-import-position
from utils.get_values import get_values, get_local_values, get_multiple_values, get_vis_vals
from utils.clear_file import clear_selected_single_file, clear_selected_local_file
from utils.directory import (
    choose_file,
    choose_local_file,
    choose_output_dir,
    choose_local_output_dir,
    choose_input_dir_multi,
    choose_output_dir_multi,
)
from utils.object_change import handle_standard_object_change, handle_local_object_change
from utils.non_polymer import show_warning_dialog
from utils.residues import get_residue_range, update_residue_range
from utils.helpers import update_chain_combo_box, init_timers, object_exists
from utils.config import SECTION_STYLESHEET
from utils.updates import (
    update_list,
    update_local_list,
    update_output_widgets,
    update_output_widgets_local,
    update_output_widgets_multi,
)
from utils.trajectory import select_mol_file, select_xtc_file, export_frames_from_traj

from analysis.local_ct_analysis import run_local_ct
from analysis.single_file_analysis import run_standard_analysis
from analysis.single_frame_analysis import run_single_frame_analysis, toggle_frame_controls
from analysis.multiple_file_analysis import run_multi_analysis
from analysis.visualization import visualize_molecule

from tabs.local_tab import init_local_tab
from tabs.single_file_tab import init_single_file_tab
from tabs.multiple_file_tab import init_multi_file_tab

# Extend PyMOL command set with a helper if missing; allows other modules to use cmd.object_exists
if not hasattr(cmd, "object_exists"):
    setattr(cmd, "object_exists", object_exists)


class CTDialog(QtWidgets.QDialog):
    """
    Primary Qt dialog for the Circuit Topology Tool.

    The dialog acts largely as a dispatcher: Qt slots are defined as methods on
    this class and immediately forward the call to specialized functions in
    the plugin's `utils` and `analysis` packages. This separation keeps the
    UI code lightweight and testable.

    Attributes
    ----------
    current_objects : set
        Set of object names present in the standard (non-local) object dropdown.
    current_local_objects : set
        Set of object names present in the local object dropdown.
    tab_widget : QtWidgets.QTabWidget
        Top-level tab container holding use-case specific tabs.
    local_tab, single_file_tab, multi_file_tab : QtWidgets.QWidget
        Tab pages created and initialized during UI setup.
    """

    # --- Thin wrapper slots delegating to helper functions (get_values group) ---
    @QtCore.pyqtSlot()
    def get_values(self):
        """Return settings from the single-file tab UI controls."""
        return get_values(self)

    @QtCore.pyqtSlot()
    def get_local_values(self):
        """Return settings from the local analysis tab UI controls."""
        return get_local_values(self)

    @QtCore.pyqtSlot()
    def get_multiple_values(self):
        """Return settings from the multi-file analysis tab UI controls."""
        return get_multiple_values(self)

    @QtCore.pyqtSlot()
    def get_vis_vals(self):
        """Return visualization-specific values from the UI."""
        return get_vis_vals(self)

    # --- File clearing helpers ---
    @QtCore.pyqtSlot()
    def clear_selected_local_file(self):
        """Clear the selected local file control value(s)."""
        clear_selected_local_file(self)

    @QtCore.pyqtSlot()
    def clear_selected_single_file(self):
        """Clear the selected single-file control value(s)."""
        clear_selected_single_file(self)

    # --- Directory / file chooser wrappers ---
    @QtCore.pyqtSlot()
    def choose_file(self):
        """Open a file chooser to select a single input file (single-file tab)."""
        choose_file(self)

    @QtCore.pyqtSlot()
    def choose_local_file(self):
        """Open a file chooser to select a local PDB/file for local analysis."""
        choose_local_file(self)

    @QtCore.pyqtSlot()
    def choose_output_dir(self):
        """Open a directory chooser for specifying the output folder (single-file)."""
        choose_output_dir(self)

    @QtCore.pyqtSlot()
    def choose_local_output_dir(self):
        """Open a directory chooser for specifying the output folder (local analysis)."""
        choose_local_output_dir(self)

    @QtCore.pyqtSlot()
    def choose_input_dir_multi(self):
        """Open a directory chooser for selecting multiple input files (multi-file)."""
        choose_input_dir_multi(self)

    @QtCore.pyqtSlot()
    def choose_output_dir_multi(self):
        """Open a directory chooser for specifying the output folder (multi-file)."""
        choose_output_dir_multi(self)

    # --- Object change handlers ---
    @QtCore.pyqtSlot()
    def handle_local_object_change(self, obj_name: Optional[str]=None):
        """
        Handle changes in the local object dropdown.

        Parameters
        ----------
        obj_name : Optional[str]
            Explicit object name to handle. If None, the value is read from the UI.
        """
        if obj_name is None:
            obj_name = self.local_dropdown_objects.currentText()
        handle_local_object_change(self, obj_name)

    @QtCore.pyqtSlot()
    def handle_standard_object_change(self, obj_name: Optional[str]=None):
        """
        Handle changes in the standard object dropdown.

        Parameters
        ----------
        obj_name : Optional[str]
            Explicit object name to handle. If None, the value is read from the UI.
        """
        if obj_name is None:
            obj_name = self.dropdown_objects.currentText()
        handle_standard_object_change(self, obj_name)

    # --- Non-polymer warnings ---
    @QtCore.pyqtSlot()
    def show_warning_dialog(self):
        """Display a warning dialog when a non-polymeric selection is detected."""
        show_warning_dialog(self)

    # --- Residue range helpers ---
    @QtCore.pyqtSlot()
    def get_residue_range(self, obj_name: Optional[str]=None):
        """
        Request the residue range for an object and update the UI.

        Parameters
        ----------
        obj_name : Optional[str]
            The object to query. If not supplied, reads from the local object dropdown.
        """
        if obj_name is None:
            obj_name = self.local_dropdown_objets.currentText()
        get_residue_range(self, obj_name)

    @QtCore.pyqtSlot()
    def update_residue_range(self):
        """Apply the current residue-range widget values to the model or internal state."""
        update_residue_range(self)

    # --- Helper wrappers ---
    @QtCore.pyqtSlot()
    def update_chain_combo_box(self):
        """Refresh the chain selection combobox based on the currently selected object."""
        update_chain_combo_box(self)

    @QtCore.pyqtSlot()
    def init_timers(self):
        """Initialize any repeating timers used by the GUI (e.g., polling PyMOL state)."""
        init_timers(self)

    # --- UI update wrappers ---
    @QtCore.pyqtSlot()
    def update_list(self):
        """Refresh the object list shown in the single-file tab."""
        update_list(self)

    @QtCore.pyqtSlot()
    def update_local_list(self):
        """Refresh the object list shown in the local-analysis tab."""
        update_local_list(self)

    @QtCore.pyqtSlot()
    def update_output_widgets(self):
        """Update widgets that display or depend on the output path (single-file)."""
        update_output_widgets(self)

    @QtCore.pyqtSlot()
    def update_output_widgets_local(self):
        """Update widgets that display or depend on the output path (local-analysis)."""
        update_output_widgets_local(self)

    @QtCore.pyqtSlot()
    def update_output_widgets_multi(self):
        """Update widgets that display or depend on the output path (multi-file)."""
        update_output_widgets_multi(self)

    # --- Trajectory helpers ---
    @QtCore.pyqtSlot()
    def select_mol_file(self):
        """Select a molecular file used by the trajectory tools."""
        select_mol_file(self)

    @QtCore.pyqtSlot()
    def select_xtc_file(self):
        """Select an XTC (trajectory) file used by the trajectory tools."""
        select_xtc_file(self)

    @QtCore.pyqtSlot()
    def export_frames_from_traj(self):
        """Export frames from an opened trajectory according to UI parameters."""
        export_frames_from_traj(self)

    # --- Tab initializers ---
    @QtCore.pyqtSlot()
    def init_local_tab(self):
        """Initialize widgets and layout for the local analysis tab."""
        init_local_tab(self)

    @QtCore.pyqtSlot()
    def init_single_file_tab(self):
        """Initialize widgets and layout for the single-file analysis tab."""
        init_single_file_tab(self)

    @QtCore.pyqtSlot()
    def init_multi_file_tab(self):
        """Initialize widgets and layout for the multi-file analysis tab."""
        init_multi_file_tab(self)

    # --- Analysis entrypoints ---
    @QtCore.pyqtSlot()
    def run_local_ct(self):
        """Run local circuit-topology analysis using current local-tab settings."""
        run_local_ct(self)

    @QtCore.pyqtSlot()
    def run_standard_analysis(self):
        """Run the standard single-file analysis flow using current UI settings."""
        run_standard_analysis(self)

    @QtCore.pyqtSlot()
    def run_single_frame_analysis(self):
        """Run an analysis for the currently selected single frame."""
        run_single_frame_analysis(self)

    @QtCore.pyqtSlot()
    def run_multi_analysis(self):
        """Run the batch multi-file analysis flow."""
        run_multi_analysis(self)

    @QtCore.pyqtSlot()
    def visualize_molecule(self, contact_type: str):
        """
        Trigger molecule visualization in PyMOL.

        Parameters
        ----------
        contact_type : str
            Identifier describing the visualization type to render.
        """
        visualize_molecule(self, contact_type)

    @QtCore.pyqtSlot(bool)
    def toggle_frame_controls(self, enabled: bool):
        """
        Enable or disable UI controls that affect frame selection.

        Parameters
        ----------
        enabled : bool
            Whether the frame-related controls should be enabled.
        """
        toggle_frame_controls(self, enabled=enabled)

    # --- Construction and UI lifecycle ---
    def __init__(self, parent=None):
        """
        Construct the dialog and perform UI initialization.

        The constructor sets up minimal dialog properties and calls `init_ui`
        to construct the widget tree. Timers are initialized after widgets so
        that they operate on valid UI controls.
        """
        super().__init__(parent)

        # Maintain sets of observed object names to avoid redundant UI updates
        self.current_objects = set()
        self.current_local_objects = set()

        # Dialog appearance
        self.setWindowTitle("Circuit Topology Tool")
        self.setGeometry(100, 100, 480, 540)
        self.setStyleSheet(SECTION_STYLESHEET)

        # Build and initialize UI
        self.init_ui()
        self.init_timers()

    def init_ui(self):
        """Create the top-level tab widget and initialize each feature tab."""
        self.tab_widget = QtWidgets.QTabWidget()

        # Create tab containers (content populated by respective init_* functions)
        self.local_tab = QtWidgets.QWidget()
        self.single_file_tab = QtWidgets.QWidget()
        self.multi_file_tab = QtWidgets.QWidget()

        # Add tabs with descriptive labels (user-facing)
        self.tab_widget.addTab(self.local_tab, "Local Circuit Topology")
        self.tab_widget.addTab(self.single_file_tab, "Single‑File Analysis")
        self.tab_widget.addTab(self.multi_file_tab, "Multi‑File Analysis")

        # Populate each tab via modular initializers
        self.init_local_tab()
        self.init_single_file_tab()
        self.init_multi_file_tab()

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)
