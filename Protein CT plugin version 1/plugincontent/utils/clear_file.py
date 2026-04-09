from pymol import cmd
from pymol.Qt import QtWidgets

def clear_selected_single_file(self: QtWidgets.QWidget) -> None:
    """
    Clears the selected single file from PyMOL and UI.
    
    Args:
        self: The QtWidget object (CTDialog instance) calling this function.
    """
    if hasattr(self, "selected_obj_name") and cmd.object_exists(self.selected_obj_name):
        cmd.delete(self.selected_obj_name)
    self.selected_file = None
    self.dir_label.setText("No file selected")
    self.dropdown_objects.setCurrentIndex(0)
    self.update_list()

def clear_selected_local_file(self: QtWidgets.QWidget) -> None:
    """
    Clears the selected local file from PyMOL and UI.
    
    Args:
        self: The QtWidget object (CTDialog instance) calling this function.
    """
    if hasattr(self, "local_selected_obj_name") and cmd.object_exists(self.local_selected_obj_name):
        cmd.delete(self.local_selected_obj_name)
    self.local_selected_file = None
    self.local_dir_label.setText("No file selected…")
    self.local_dropdown_objects.clear()
    self.local_dropdown_objects.addItem("Select a file.")
    self.chain_combo_box.clear()
    self.box_res_id.setRange(0, 0)
    self.box_res_id.setValue(0)
    self.update_local_list()