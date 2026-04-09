from pymol import cmd
from pymol.Qt import QtWidgets

def update_output_widgets_multi(self: QtWidgets.QWidget) -> None:
    """
    Updates the visibility of multi-file output widgets based on checkboxes.
    
    Args:
        self: The QtWidget object.
    """
    show = (
            self.checkbox_export_cmap3_multi.isChecked() or self.checkbox_export_matrix_multi.isChecked() or self.checkbox_export_psc_multi.isChecked())
    self.output_txt_multi.setVisible(show)
    self.output_dir_button_multi.setVisible(show)
    self.output_dir_label_multi.setVisible(show)

def update_output_widgets_local(self: QtWidgets.QWidget) -> None:
    """
    Updates the visibility of local CT output widgets based on checkboxes.
    
    Args:
        self: The QtWidget object.
    """
    show = (
            self.checkbox_local_matrix.isChecked() or self.checkbox_local_cmap3.isChecked())
    self.output_local_txt.setVisible(show)
    self.output_local_button.setVisible(show)
    self.output_local_label.setVisible(show)

def update_output_widgets(self: QtWidgets.QWidget) -> None:
    """
    Updates the visibility of standard analysis output widgets based on checkboxes.
    
    Args:
        self: The QtWidget object.
    """
    show = self.checkbox_export_cmap3.isChecked() or self.checkbox_export_matrix.isChecked() or self.checkbox_export_matrix_multi.isChecked() or self.checkbox_export_cmap3_multi.isChecked() or self.checkbox_export_psc_multi.isChecked() or self.checkbox_local_cmap3.isChecked() or self.checkbox_local_matrix.isChecked()
    self.output_txt.setVisible(show)
    self.output_dir_button.setVisible(show)
    self.output_dir_label.setVisible(show)

def update_local_list(self: QtWidgets.QWidget) -> None:
    """
    Updates the list of local objects from PyMOL.
    
    Args:
        self: The QtWidget object.
    """
    all_objects = cmd.get_names('all')
    new_objects = [obj for obj in all_objects if cmd.get_type(obj) in ('object:molecule', 'selection')]

    if new_objects != self.current_local_objects:
        self.current_local_objects = new_objects

        selection = self.local_dropdown_objects.currentText()
        self.local_dropdown_objects.clear()
        if selection in self.current_local_objects:
            self.local_dropdown_objects.setCurrentText(selection)
        self.local_dropdown_objects.addItems(["Select a file."])
        self.local_dropdown_objects.addItems(self.current_local_objects)

def update_list(self: QtWidgets.QWidget) -> None:
    """
    Updates the list of objects from PyMOL.
    
    Args:
        self: The QtWidget object.
    """
    all_objects = cmd.get_names('all')
    new_objects = [obj for obj in all_objects if cmd.get_type(obj) in ('object:molecule', 'selection')]

    if new_objects != self.current_objects:
        self.current_objects = new_objects

        selection = self.dropdown_objects.currentText()
        self.dropdown_objects.clear()
        if selection in self.current_objects:
            self.dropdown_objects.setCurrentText(selection)
        self.dropdown_objects.addItems(["Select a file."])
        self.dropdown_objects.addItems(self.current_objects)