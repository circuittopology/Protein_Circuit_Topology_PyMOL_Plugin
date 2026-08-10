"""
GUI class and bindings for the Circuit Topology PyMOL plugin.

This module exposes the CTDialog class that encapsulates the Qt-based GUI used
to drive the plugin. The design follows a thin-wrapper pattern where GUI
slots delegate behavior to functions implemented in modular helper and analysis
submodules. This keeps the dialog class focused on UI wiring and lifecycle
management while the rest is in reusable utilities.

Key responsibilities:
- Provide a persistent dialog instance that can be shown by the plugin entrypoint.
- Expose Qt slots that delegate to functions defined in the plugin's utilities.
- Manage UI initialization, timers and basic dialog state.
"""

from PyQt5.QtWidgets import QDialog, QTabWidget, QVBoxLayout

from tabs.local_tab import LocalTab
from tabs.multiple_file_tab import MultiFileTab
from tabs.single_file_tab import SingleFileTab
from utils.config import SECTION_STYLESHEET
from utils.pymol_objects import PymolObjects
from utils.updates import update_list, update_local_list


class CTDialog(QDialog):
    """
    Primary Qt dialog for the Circuit Topology Tool.

    Attributes
    ----------
    tab_widget : QTabWidget
        Top-level tab container.
    local_tab, single_file_tab, multi_file_tab : QWidget
        The three feature tabs, each self-contained.
    pymol_objects : PymolObjects
        Shared poller for the PyMOL object list.
    _suppress_non_polymer_warning : bool
        Session-wide "don't show again" flag, set via utils.non_polymer.
    """

    def __init__(self, parent=None):
        """Construct the dialog: window chrome, the three tabs, then the shared object model."""
        super().__init__(parent)

        self.setWindowTitle("Circuit Topology Tool")
        self.setGeometry(100, 100, 480, 540)
        self.setStyleSheet(SECTION_STYLESHEET)

        self.init_ui()

        self.pymol_objects = PymolObjects(self)
        self.pymol_objects.changed.connect(self._on_objects_changed)
        self.pymol_objects.refresh()

    def _on_objects_changed(self, objects):
        """Refresh both object dropdowns from one polled list."""
        update_list(self.single_file_tab, objects)
        update_local_list(self.local_tab, objects)

    def closeEvent(self, event):  # noqa: N802
        """Stop polling when the dialog closes."""
        if getattr(self, "pymol_objects", None) is not None:
            self.pymol_objects.stop()
        super().closeEvent(event)

    def init_ui(self):
        """Create the top-level tab widget and initialize each feature tab."""
        self.tab_widget = QTabWidget()

        self.local_tab = LocalTab(self)
        self.single_file_tab = SingleFileTab(self)
        self.multi_file_tab = MultiFileTab(self)

        self.tab_widget.addTab(self.local_tab, "Local Circuit Topology")
        self.tab_widget.addTab(self.single_file_tab, "Single‑File Analysis")  # noqa: RUF001
        self.tab_widget.addTab(self.multi_file_tab, "Multi‑File Analysis")  # noqa: RUF001

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)
