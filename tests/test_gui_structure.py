"""Structural tests for the split of CTDialog into a parent plus three tab widgets.

"""
from tabs.local_tab import LocalTab
from tabs.multiple_file_tab import MultiFileTab
from tabs.single_file_tab import SingleFileTab


def test_each_tab_is_its_own_widget(ct_dialog):
    assert isinstance(ct_dialog.local_tab, LocalTab)
    assert isinstance(ct_dialog.single_file_tab, SingleFileTab)
    assert isinstance(ct_dialog.multi_file_tab, MultiFileTab)
    assert ct_dialog.tab_widget.count() == 3

def test_no_tab_offers_to_delete_the_users_atoms(ct_dialog):
    """Non-polymer atoms are excluded by selection now."""
    from PyQt5.QtWidgets import QPushButton

    for tab in (ct_dialog.local_tab, ct_dialog.single_file_tab, ct_dialog.multi_file_tab):
        labels = [b.text().lower() for b in tab.findChildren(QPushButton)]
        assert not any("non-polymer" in text for text in labels), (
            f"{type(tab).__name__} still offers to delete atoms: {labels}"
        )

def test_the_polling_model_is_shared_by_every_tab(ct_dialog):
    """One model and one timer across all tabs. Reduces compute."""
    model = ct_dialog.pymol_objects
    assert model is not None
    for tab in (ct_dialog.local_tab, ct_dialog.single_file_tab, ct_dialog.multi_file_tab):
        assert tab.pymol_objects is model


def test_closing_the_dialog_stops_polling(qapp):
    """run_plugin_gui builds a new dialog when the old one is hidden; the old timer must not live on."""
    from gui_class import CTDialog

    dlg = CTDialog()
    try:
        assert dlg.pymol_objects._timer.isActive()
        dlg.close()
        assert not dlg.pymol_objects._timer.isActive()
    finally:
        dlg.deleteLater()
