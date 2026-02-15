import sys
from pathlib import Path
from pymol import cmd
from pymol.Qt import QtWidgets, QtCore
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
# pylint: disable=wrong-import-position
from utils.config import INFO_BUTTON_STYLE

def update_chain_combo_box(self):
    self.chain_combo_box.clear()
    self.chain_combo_box.addItems(self.curr_chain_residues.keys())

def make_info_button(tooltip: str):
    btn = QtWidgets.QPushButton("ⓘ")
    btn.setFixedWidth(20)
    btn.setFlat(True)
    btn.setStyleSheet(INFO_BUTTON_STYLE)
    btn.setToolTip(tooltip)
    return btn

def init_timers(self):
    self.timer = QtCore.QTimer(self)
    self.timer.timeout.connect(self.update_list)
    self.timer.timeout.connect(self.update_local_list)
    self.timer.start(1000)

def object_exists(name):
    return name in cmd.get_names()
