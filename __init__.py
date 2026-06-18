"""
Plugin package initializer for the Circuit Topology PyMOL plugin.

This module is the canonical PyMOL plugin entrypoint. PyMOL calls the
`__init_plugin__` function when it loads the plugin, and this function
is responsible for preparing the environment, attempting automated
dependency installation (if needed), registering PyMOL commands, and
exposing the GUI entry point via the PyMOL plugins menu.

Dependencies are installed exclusively through PyMOL's own conda
environment (no pip, no package-manager mixing) and only when the running
session can actually write to that environment.
"""

import importlib
import logging
import platform
import sys
from pathlib import Path

from pymol.plugins import addmenuitemqt

PROJECT_ROOT = Path(__file__).resolve().parents[0]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from initialization_checks import (
    PYMOL_ENV,
    REQUIREMENTS_FILE,
    check_installed_packages,
    get_requirements,
    install_dependencies,
    install_failed,
    is_path_user,
    is_running_as_admin,
    register_pymol_functions,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def _show_admin_required_dialog() -> None:
    """Show a Qt message box explaining that elevated privileges are required."""
    try:
        from PyQt5.QtWidgets import QApplication, QMessageBox
        app = QApplication.instance()
        if app is None:
            return

        system = platform.system()
        if system == "Windows":
            hint = (
                'Please close PyMOL, right-click it and choose "Run as administrator", '
                "then load the plugin again."
            )
        elif system == "Darwin":
            hint = (
                "Please relaunch PyMOL from an administrator account, or reinstall PyMOL "
                'for your user only (the recommended "Just Me" option), then load the '
                "plugin again."
            )
        else:
            hint = (
                "Please relaunch PyMOL with sufficient privileges (for example via sudo), "
                "or reinstall PyMOL for your user only, then load the plugin again."
            )

        msg = QMessageBox()
        msg.setWindowTitle("Elevated privileges required")
        msg.setIcon(QMessageBox.Warning)
        msg.setText(
            "Automatic dependency installation could not proceed because PyMOL is "
            "installed system-wide and this session does not have the required "
            "privileges.\n\n" + hint,
        )
        msg.exec_()
    except Exception:
        logger.exception("Failed to show admin required dialog")


def _show_restart_required_dialog() -> None:
    """Tell the user dependencies were installed but PyMOL must be restarted."""
    try:
        from PyQt5.QtWidgets import QApplication, QMessageBox
        app = QApplication.instance()
        if app is None:
            return
        msg = QMessageBox()
        msg.setWindowTitle("Restart required")
        msg.setIcon(QMessageBox.Information)
        msg.setText(
            "The required dependencies were installed successfully, but PyMOL needs to be "
            "restarted before the plugin can be used.\n\n"
            "Please close and reopen PyMOL, then open the plugin again.",
        )
        msg.exec_()
    except Exception:
        logger.exception("Failed to show restart required dialog")


def _try_register() -> bool:
    """Attempt to register plugin functions and add the GUI menu item."""
    try:
        register_pymol_functions()
        addmenuitemqt("Protein Circuit Topology Plugin", run_plugin_gui)
    except ImportError:
        logger.debug("Registration failed — missing dependencies")
        return False
    else:
        logger.info("ProteinCT plugin initialized")
        return True


def __init_plugin__(app=None):  # noqa: ARG001, N807
    """
    Initialize the plugin within PyMOL.

    Invoked by PyMOL when the plugin is loaded. The flow is:
      1. Register PyMOL commands if dependencies are already present.
      2. Otherwise, if PyMOL is installed system-wide and this session lacks
         administrator/root privileges, show guidance and stop (a writable
         environment is required to install).
      3. Install the missing dependencies into PyMOL's own conda environment.
      4. Invalidate the import cache and re-register. If the freshly installed
         packages are not importable in this live session, ask the user to
         restart PyMOL.

    Notes
    -----
    - The same privilege gate is applied uniformly on Windows, Linux and macOS.
    - The function never elevates privileges itself and never mixes package
      managers — installation goes through conda only.
    """
    logger.info("Beginning ProteinCT plugin initialization")

    # Dependencies may already be present.
    if _try_register():
        return

    # A system-wide install needs admin/root to write into PyMOL's environment.
    if not is_path_user(PYMOL_ENV) and not is_running_as_admin():
        logger.info(
            "PyMOL is installed system-wide and this session lacks administrator/root "
            "privileges; automated dependency installation cannot proceed.",
        )
        _show_admin_required_dialog()
        install_failed(reqs=REQUIREMENTS_FILE)
        return

    # Log what needs installing.
    requirements_list = get_requirements(req_path=REQUIREMENTS_FILE)
    _, packs = check_installed_packages(requirements_list)
    logger.info("Packages to install for ProteinCT plugin: %s", packs)

    # Install into PyMOL's own conda environment, then retry registration.
    if install_dependencies():
        importlib.invalidate_caches()
        if _try_register():
            return
        # Installed on disk, but not importable in this already-running session.
        _show_restart_required_dialog()
        return

    install_failed(reqs=REQUIREMENTS_FILE)


# Persistent dialog instance used to avoid creating multiple windows
DIALOG_INSTANCE = None


def run_plugin_gui():
    """
    Create or raise the plugin GUI dialog.

    This function is bound as the menu action entrypoint and returns the
    singleton dialog instance so callers (and tests) can interact with it.
    """
    from gui_class import CTDialog
    global DIALOG_INSTANCE  # noqa: PLW0603
    if DIALOG_INSTANCE is None or not DIALOG_INSTANCE.isVisible():
        DIALOG_INSTANCE = CTDialog()
        DIALOG_INSTANCE.show()
    else:
        DIALOG_INSTANCE.raise_()
        DIALOG_INSTANCE.activateWindow()

    return DIALOG_INSTANCE
