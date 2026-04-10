"""
Utility functions for updating GUI elements in the PyMOL plugin.
"""
from typing import Any, List, Optional

from pymol import cmd


def update_output_widgets_multi(self: Any) -> None:
    """
    Updates the visibility of output widgets in the multi-file analysis
    tab based on checkbox states.

    Args:
        self: The main GUI class instance.
    """
    cmap_check = self.checkbox_export_cmap3_multi.isChecked()
    matrix_check = self.checkbox_export_matrix_multi.isChecked()
    psc_check = self.checkbox_export_psc_multi.isChecked()

    show = (cmap_check or matrix_check or psc_check)

    self.output_txt_multi.setVisible(show)
    self.output_dir_button_multi.setVisible(show)
    self.output_dir_label_multi.setVisible(show)

def update_output_widgets_local(self: Any) -> None:
    """
    Updates the visibility of output widgets in the local analysis tab based on checkbox states.

    Args:
        self: The main GUI class instance.
    """
    show = (
            self.checkbox_local_matrix.isChecked() or self.checkbox_local_cmap3.isChecked())
    self.output_local_txt.setVisible(show)
    self.output_local_button.setVisible(show)
    self.output_local_label.setVisible(show)

def update_output_widgets(self: Any) -> None:
    """
    Update visibility of output widgets for single-file export options.
    """
    show = (
        self.checkbox_export_cmap3.isChecked()
        or self.checkbox_export_matrix.isChecked()
    )
    self.output_txt.setVisible(show)
    self.output_dir_button.setVisible(show)
    self.output_dir_label.setVisible(show)

def update_local_list(self: Any, new_objects: Optional[List[str]] = None) -> None:
    """
    Updates the list of available objects in the local analysis dropdown.

    Args:
        self: The main GUI class instance.
        new_objects: Pre-fetched object list. If None, queries PyMOL.
    """
    if new_objects is None:
        new_objects = cmd.get_object_list()

    if new_objects != self.current_local_objects:
        self.current_local_objects = new_objects

        selection = self.local_dropdown_objects.currentText()
        self.local_dropdown_objects.clear()
        if selection in self.current_local_objects:
            self.local_dropdown_objects.setCurrentText(selection)
        self.local_dropdown_objects.addItems(["Select a file."])
        self.local_dropdown_objects.addItems(self.current_local_objects)

def update_list(self: Any, new_objects: Optional[List[str]] = None) -> None:
    """
    Updates the list of available objects in the single-file analysis dropdown.

    Args:
        self: The main GUI class instance.
        new_objects: Pre-fetched object list. If None, queries PyMOL.
    """
    if new_objects is None:
        new_objects = cmd.get_object_list()

    if new_objects != self.current_objects:
        self.current_objects = new_objects

        selection = self.dropdown_objects.currentText()
        self.dropdown_objects.clear()
        if selection in self.current_objects:
            self.dropdown_objects.setCurrentText(selection)
        self.dropdown_objects.addItems(["Select a file."])
        self.dropdown_objects.addItems(self.current_objects)