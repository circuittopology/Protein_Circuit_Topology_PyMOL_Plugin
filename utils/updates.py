"""
Utility functions for updating GUI elements in the PyMOL plugin.
"""
from pymol import cmd

PYMOL_OBJ = ('object:molecule', 'selection')

def update_output_widgets_multi(self):
    """
    Update visibility of output widgets for multi-file export options.
    """
    cmap_check = self.checkbox_export_cmap3_multi.isChecked()
    matrix_check = self.checkbox_export_matrix_multi.isChecked()
    psc_check = self.checkbox_export_psc_multi.isChecked()

    show = (cmap_check or matrix_check or psc_check)

    self.output_txt_multi.setVisible(show)
    self.output_dir_button_multi.setVisible(show)
    self.output_dir_label_multi.setVisible(show)

def update_output_widgets_local(self):
    """
    Update visibility of output widgets for local CT analysis options.
    """
    show = (self.checkbox_local_matrix.isChecked() or self.checkbox_local_cmap3.isChecked())
    self.output_local_txt.setVisible(show)
    self.output_local_button.setVisible(show)
    self.output_local_label.setVisible(show)

def update_output_widgets(self):
    """
    Update visibility of output widgets for single-file export options.
    """
    show = (
        self.checkbox_export_cmap3.isChecked()
        or self.checkbox_export_matrix.isChecked()
        or self.checkbox_export_matrix_multi.isChecked()
        or self.checkbox_export_cmap3_multi.isChecked()
        or self.checkbox_export_psc_multi.isChecked()
        or self.checkbox_local_cmap3.isChecked()
        or self.checkbox_local_matrix.isChecked()
    )
    self.output_txt.setVisible(show)
    self.output_dir_button.setVisible(show)
    self.output_dir_label.setVisible(show)

def update_local_list(self):
    """
    Update the list of local objects in PyMOL available for local CT analysis.
    """
    all_objects = cmd.get_names('all')
    new_objects = [obj for obj in all_objects if cmd.get_type(obj) in PYMOL_OBJ]

    if new_objects != self.current_local_objects:
        self.current_local_objects = new_objects

        selection = self.local_dropdown_objects.currentText()
        self.local_dropdown_objects.clear()
        if selection in self.current_local_objects:
            self.local_dropdown_objects.setCurrentText(selection)
        self.local_dropdown_objects.addItems(["Select a file."])
        self.local_dropdown_objects.addItems(self.current_local_objects)

def update_list(self):
    """
    Update the list of objects in PyMOL available for single-file analysis.
    """
    all_objects = cmd.get_names('all')
    new_objects = [obj for obj in all_objects if cmd.get_type(obj) in PYMOL_OBJ]

    if new_objects != self.current_objects:
        self.current_objects = new_objects

        selection = self.dropdown_objects.currentText()
        self.dropdown_objects.clear()
        if selection in self.current_objects:
            self.dropdown_objects.setCurrentText(selection)
        self.dropdown_objects.addItems(["Select a file."])
        self.dropdown_objects.addItems(self.current_objects)
