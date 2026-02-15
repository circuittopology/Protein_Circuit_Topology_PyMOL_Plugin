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

import os
from pathlib import Path
import sys
# pylint: disable=import-error, no-name-in-module, wrong-import-position
from pymol.plugins import addmenuitemqt

PROJECT_ROOT = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(PROJECT_ROOT))
# Import platform-aware installation and registration utilities
from initialization_checks import *  # brings register_pymol_functions, install helpers, etc.

# Determine environment and requirement locations
PYMOL_ENV_PATH = sys.executable
PYMOL_ENV = os.path.dirname(PYMOL_ENV_PATH)
PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS_FILE = os.path.join(PLUGIN_DIR, "requirements.yml")


def __init_plugin__(app=None):
    """
    Initialize the plugin within PyMOL.

    This function is invoked by PyMOL when the plugin is loaded. It tries the
    following steps, in order:
      1. Parse requirements and determine what is missing.
      2. Register PyMOL commands if possible.
      3. If registration fails, attempt to install dependencies using:
         - PyMOL's internal conda (via `pymol_install`)
         - Platform-specific installers (`win_install`, `mac_install`, `linux_install`)
      4. If installation succeeds, register commands and add the menu item to
         open the GUI.

    Notes
    -----
    - The function prints stateful diagnostic messages to the PyMOL console.
    - The automated install path will be skipped when PyMOL is installed in a
      system location that requires admin privileges (unless running as admin).
    """
    print("Beginning ProteinCT plugin initialization")

    auto_install = True

    # If developer toggles `auto_install` to False, attempt registration without installs.
    if auto_install is False:
        try:
            print('Checking ProteinCT plugin initialization')
            register_pymol_functions()

            addmenuitemqt('Protein Circuit Topology Plugin', run_plugin_gui)

            print('ProteinCT plugin initialized')
            return
        except Exception:
            install_failed(reqs=REQUIREMENTS_FILE)
            return

    # Determine installation requirements and platform
    requirements_list = get_requirements(req_path=REQUIREMENTS_FILE)
    _, packs = check_installed_packages(requirements_list)

    sys_type = platform.system()
    pymol_path_user = is_path_user(PYMOL_ENV)
    # If PyMOL is installed system-wide on non-mac platforms, automated install cannot proceed
    if pymol_path_user is False and sys_type != "Darwin":
        print("""PyMOL has been installed on the system environment path,
              automated plugin install cannot occur for ProteinCT plugin.
              """
        )
        install_failed(reqs=REQUIREMENTS_FILE)
        return
    if pymol_path_user is False and sys_type == "Darwin":
        print("""PyMOL has been installed on the system path,
              automated install will still be attempted.
              """
        )
        print("Assuming the user is an admin, automated install should succeed.")

    # First attempt: register functions as-is (no install)
    try:
        print('Checking ProteinCT plugin initialization')
        register_pymol_functions()
        addmenuitemqt('Protein Circuit Topology Plugin', run_plugin_gui)
        print('ProteinCT plugin initialized')
        return
    except Exception as e:
        print(f'Error: {e}')
        print(f"The following packages need to be installed for ProteinCT plugin: {packs}")

        # Try using PyMOL's terminal-driven conda approach
        result = pymol_install()

        if result == True:
            try:
                print('Checking ProteinCT plugin initialization')
                register_pymol_functions()
                addmenuitemqt('Protein Circuit Topology Plugin', run_plugin_gui)
                print('ProteinCT plugin initialized')
                return
            except Exception as er:
                print(f"Error: {er}")

    # If the above did not suffice, attempt platform-specific fallbacks
    try:
        print('Checking ProteinCT plugin initialization')
        register_pymol_functions()
        addmenuitemqt('Protein Circuit Topology Plugin', run_plugin_gui)
        print('ProteinCT plugin initialized')
        return
    except Exception:
        if sys_type == "Windows":
            result = win_install()
            if result:
                try:
                    register_pymol_functions()
                    addmenuitemqt('Protein Circuit Topology Plugin', run_plugin_gui)
                    print('ProteinCT plugin initialized')
                    return
                except Exception as er:
                    print(f"Error: {er}")
                    install_failed()
                    return
        elif sys_type == "Darwin":
            result = mac_install()
            if result:
                try:
                    register_pymol_functions()
                    addmenuitemqt('Protein Circuit Topology Plugin', run_plugin_gui)
                    print('ProteinCT plugin initialized')
                    return
                except Exception as er:
                    print(f"Error: {er}")
                    install_failed()
                    return
        else:
            result = linux_install()
            if result:
                try:
                    register_pymol_functions()
                    addmenuitemqt('Protein Circuit Topology Plugin', run_plugin_gui)
                    print('ProteinCT plugin initialized')
                    return
                except Exception as er:
                    print(f"Error: {er}")
                    install_failed()
                    return


# Persistent dialog instance used to avoid creating multiple windows
DIALOG_INSTANCE = None


def run_plugin_gui():
    """
    Create or raise the plugin GUI dialog.

    This function is bound as the menu action entrypoint and returns the
    singleton dialog instance so callers (and tests) can interact with it.
    """
    from gui_class import CTDialog
    global DIALOG_INSTANCE
    if DIALOG_INSTANCE is None or not DIALOG_INSTANCE.isVisible():
        DIALOG_INSTANCE = CTDialog()
        DIALOG_INSTANCE.show()
    else:
        DIALOG_INSTANCE.raise_()
        DIALOG_INSTANCE.activateWindow()

    return DIALOG_INSTANCE
