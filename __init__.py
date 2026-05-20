"""
Plugin package initializer for the Circuit Topology PyMOL plugin.

This module is the canonical PyMOL plugin entrypoint. PyMOL calls the
`__init_plugin__` function when it loads the plugin, and this function
is responsible for preparing the environment, attempting automated
dependency installation (if enabled), registering PyMOL commands, and
exposing the GUI entry point via the PyMOL plugins menu.

The module intentionally orchestrates retries of different install
strategies and prints human-readable diagnostics to assist users when
manual intervention is necessary.
"""

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
    install_failed,
    is_path_user,
    is_running_as_admin,
    linux_install,
    mac_install,
    pymol_install,
    register_pymol_functions,
    win_install,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def _show_admin_required_dialog() -> None:
    """Show a Qt message box telling the user to restart PyMOL as administrator."""
    try:
        from PyQt5.QtWidgets import QApplication, QMessageBox
        app = QApplication.instance()
        if app is None:
            return
        msg = QMessageBox()
        msg.setWindowTitle("Administrator privileges required")
        msg.setIcon(QMessageBox.Warning)
        msg.setText(
            "Automatic dependency installation could not proceed because PyMOL is installed "
            "system-wide and this session does not have administrator privileges.\n\n"
            "Please close PyMOL, right-click it and choose "
            "<b>Run as administrator</b>, then load the plugin again.",
        )
        msg.exec_()
    except Exception:
        logger.exception("Failed to show admin required dialog")


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

    This function is invoked by PyMOL when the plugin is loaded. It tries the
    following steps, in order:
      1. Register PyMOL commands if dependencies are already present.
      2. If registration fails, attempt to install dependencies using:
         - PyMOL's internal conda (via `pymol_install`)
         - Platform-specific installers (`win_install`, `mac_install`, `linux_install`)
      3. If installation succeeds, register commands and add the menu item to open the GUI.

    Notes
    -----
    - The function prints stateful diagnostic messages to the PyMOL console.
    - The automated install path will be skipped when PyMOL is installed in a
      system location that requires admin privileges (unless running as admin).
    """
    logger.info("Beginning ProteinCT plugin initialization")

    auto_install = True

    # Direct registration attempt (dependencies may already be present)
    if _try_register():
        return

    if not auto_install:
        install_failed(reqs=REQUIREMENTS_FILE)
        return

    # Check platform constraints for automated install
    sys_type = platform.system()
    pymol_path_user = is_path_user(PYMOL_ENV)

    if not pymol_path_user:
        if sys_type == "Darwin":
            logger.info(
                "PyMOL is installed on the system path (macOS); "
                "automated install will be attempted assuming admin privileges.",
            )
        elif is_running_as_admin():
            logger.info(
                "PyMOL is installed on the system path and is running as administrator; "
                "proceeding with install.",
            )
        else:
            logger.info(
                "PyMOL is installed on the system path; "
                "automated plugin install cannot proceed without administrator privileges.",
            )
            _show_admin_required_dialog()
            install_failed(reqs=REQUIREMENTS_FILE)
            return

    # Log what needs installing
    requirements_list = get_requirements(req_path=REQUIREMENTS_FILE)
    _, packs = check_installed_packages(requirements_list)
    logger.info("Packages to install for ProteinCT plugin: %s", packs)

    # Try install strategies in order: PyMOL conda, then platform-specific
    platform_installers = {"Windows": win_install, "Darwin": mac_install}
    strategies = [pymol_install, platform_installers.get(sys_type, linux_install)]

    for strategy in strategies:
        if strategy() and _try_register():
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
