"""
Installation and initialization utilities for the Circuit Topology plugin.

This module provides platform-aware helpers used by the plugin entrypoint
to:
- Inspect and parse a conda-style requirements YAML.
- Detect which packages are already available in the current PyMOL
  environment.
- Perform installation attempts by leveraging PyMOL's embedded Python,
  pip, or platform-specific tools (conda on Windows/Mac/Linux).
- Register PyMOL commands that wrap plugin functionality.

Design goals:
- Be robust in environments where PyMOL is installed system-wide vs user-only.
- Provide clear diagnostic output suitable for logging or display in the
  PyMOL terminal.
"""

import os
import subprocess
import sys
import sysconfig
import platform
import importlib.util
from typing import List, Tuple
from pymol import cmd  # pylint: disable=import-error, no-name-in-module

# Locate the pymol env
PYMOL_ENV_PATH = sys.executable
# Get env path
PYMOL_ENV = os.path.dirname(PYMOL_ENV_PATH)
# Get directory of env and requirements.yml
PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS_FILE = os.path.join(PLUGIN_DIR, "requirements.yml")

LINUX_REQS_FIXED = REQUIREMENTS_FILE.replace("\\", "/")
LINUX_ENV_FIXED = PYMOL_ENV.replace("\\", "/")

ADMIN_INIT_CMD = ["powershell.exe", "Start-Process", "powershell.exe",
                "-ArgumentList", '-ExecutionPolicy Bypass -Command "conda init"',
                "-Verb", "RunAs"]

USER_INIT_CMD = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-Command", "conda init"]

def is_path_user(path: str) -> bool:
    """
    Checks if a given path is within the user's home directory.

    Args:
        path (str): The path to check.

    Returns:
        bool: True if the path is within the user's home directory, False otherwise.
    """
    try:
        if not path:
            return False
        path = os.path.abspath(path)
        user_dir = os.path.expanduser("~")

        if platform.system() == "Windows":
            path = path.lower()
            user_dir = user_dir.lower()

        return path.startswith(user_dir)
    except (OSError, ValueError) as e:
        print(f"Warning: Could not determine if path is user-accessible: {e}")
        return False

def pymol_install(env: str = PYMOL_ENV, reqs: str = REQUIREMENTS_FILE):
    """
    Attempts to install dependencies using the PyMOL terminal and conda.

    Args:
        env (str, optional): Path to the PyMOL environment. Defaults to PYMOL_ENV.
        reqs (str, optional): Path to the requirements file. Defaults to REQUIREMENTS_FILE.
    """
    if not os.path.exists(reqs):
        print(f"Error: Requirements file not found: {reqs}")
        return

    reqs_fixed = reqs.replace("\\", "/")

    print("Using PyMOL terminal with conda to install dependencies...")

    cmd.do('conda init')
    cmd.do(f"conda env update --file {reqs_fixed}")

def install_failed(reqs: str = REQUIREMENTS_FILE) -> None:
    """
    Prints instructions for manual installation of dependencies if automated installation fails.

    Args:
        reqs (str, optional): Path to the requirements file. Defaults to REQUIREMENTS_FILE.
    """
    install_instruc_dict = {
        'pandas': 'conda install conda-forge::pandas',
        'matplotlib': 'conda install conda-forge::matplotlib',
    }

    try:
        requirements_list = get_requirements(reqs)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error reading requirements: {e}")
        return

    all_installed, not_installed = check_installed_packages(requirements_list)

    if all_installed:
        print('All packages were installed.')
        return

    if is_path_user(PYMOL_ENV):
        print("Pymol is in user directory - no admin permissions needed.")
    else:
        print("Pymol is in system directory - admin permissions may be needed.")

    print('Automated installation failed, the following packages need to be installed')
    print(f"{not_installed}")
    print("""Please note that if PyMOL is installed on the system path, then
          admin permission will be required to install packages.
          To install the required packages, run the following commands in the PyMOL terminal:""")

    for pack in not_installed:
        if pack in install_instruc_dict:
            print(install_instruc_dict[pack])
        else:
            print(f'conda install {pack}')

    print('Once all packages are installed, restart PyMOL and reinitialize the plugin.')

def get_requirements(req_path: str) -> List[str]:
    """
    Parses the requirements.yml file to get a list of required packages.

    Args:
        req_path (str): Path to the requirements file.

    Returns:
        list: A list of package names.
    """
    if not os.path.exists(req_path):
        raise FileNotFoundError(f"Requirements file not found: {req_path}")

    packages = []
    in_dependencies = False
    try:
        with open(req_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                try:
                    stripped = line.strip()

                    if not stripped or stripped.startswith('#'):
                        continue

                    if stripped == 'channels:':
                        in_dependencies = False
                        continue

                    if stripped == 'dependencies:':
                        in_dependencies = True
                        continue

                    if in_dependencies and stripped.startswith('-'):
                        pack = stripped.replace('- ', '')
                        pack = pack.split('==')[0].split('>=')[0].split('<=')[0]
                        pack = pack.strip()
                        if pack and pack not in packages:
                            packages.append(pack)
                except Exception as e:
                    raise ValueError(
                        f"Error parsing requirements file at line {line_num}: {e}"
                    ) from e
    except UnicodeDecodeError as e:
        raise ValueError(f"Unable to read requirements file (encoding issue): {e}") from e

    if not packages:
        print("Warning: No packages found in requirements file")
    return packages


def check_installed_packages(requirements_list: List[str]) -> Tuple[bool, List[str]]:
    """
    Checks if the required packages are installed in the current environment.

    Args:
        requirements_list (list): List of package names to check.

    Returns:
        tuple[bool, list]:
            True if all installed, False otherwise,
            and a list of packages (missing if False, installed if True).
    """
    not_installed = []
    installed = []

    for pack in requirements_list:
        try:
            if importlib.util.find_spec(pack) is not None:
                installed.append(pack)
            else:
                not_installed.append(pack)
        except (ImportError, ValueError, ModuleNotFoundError):
            try:
                __import__(pack)
                installed.append(pack)
            except ImportError:
                not_installed.append(pack)

    all_installed = len(not_installed) == 0
    return all_installed, not_installed if not all_installed else installed


def is_conda_installed() -> Tuple[bool, str]:
    """
    Checks if conda is installed on the system.

    Returns:
        tuple[bool, str]: 
            A tuple containing a boolean (True if installed) 
            and the path to conda (or error message).
    """
    command = 'where conda' if platform.system() == 'Windows' else 'which conda'

    try:
        pipe = subprocess.PIPE
        result = subprocess.run(
            command, shell=True, check=True, stdout=pipe, stderr=pipe, text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, str(e)


def conda_init(user_install: bool) -> bool:
    """
    Initializes conda for PowerShell.

    Args:
        user_install (bool): True if PyMOL is installed in a user directory, False otherwise.

    Returns:
        bool: True if initialization was successful, False otherwise.
    """
    try:
        if not user_install:
            result = subprocess.run(ADMIN_INIT_CMD, check=True, capture_output=True, text=True)
        else:
            result = subprocess.run(USER_INIT_CMD, check=True, capture_output=True, text=True)

        print(f'Initialization results output: {result.stdout}')
        if result.stderr:
            print(f'Initialization results error: {result.stderr}')

        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print('Conda initialization timed out')
        return False
    except OSError as e:
        print(f'Error in intialization of conda: {e}')
        return False

def win_install(env: str = PYMOL_ENV, reqs: str = REQUIREMENTS_FILE) -> bool:
    """
    Performs installation on Windows using PowerShell and conda.

    Args:
        env (str, optional): Path to the PyMOL environment. Defaults to PYMOL_ENV.
        reqs (str, optional): Path to the requirements file. Defaults to REQUIREMENTS_FILE.

    Returns:
        bool: True if installation was successful, False otherwise.
    """
    if not os.path.exists(reqs):
        print(f"Error: Requirements file not found: {reqs}")
        return False

    conda_installed, path = is_conda_installed()
    if not conda_installed:
        print("Error: Conda not found on system")
        return False
    conda_path = path.strip() if path else ""
    conda_user_path = is_path_user(conda_path)
    conda_initialized = conda_init(user_install=conda_user_path)

    if not conda_initialized:
        return False

    reqs_fixed = reqs.replace("\\", "/")
    win_cmds = f'conda env update --file "{reqs_fixed}"'

    admin_cmd = ["powershell.exe", "Start-Process", "powershell.exe",
                 "-ArgumentList", f'-ExecutionPolicy Bypass -Command "{win_cmds}"',
                 "-Verb", "RunAs", "-Wait"]
    user_cmd = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-Command", win_cmds]
    try:
        if not conda_user_path:
            print("Running installation with admin privileges...")
            result = subprocess.run(admin_cmd, check=True, capture_output=True, text=True)
        else:
            print("Running installation with user privileges...")
            result = subprocess.run(user_cmd, check=True, capture_output=True, text=True)
        print(f"Installation output: {result.stdout}")
        if result.stderr:
            print(f"Installation warnings/errors: {result.stderr}")

        success = result.returncode == 0
        if success:
            print("Installation completed successfully.")
        else:
            print("Installation failed. Please check the output for details.")
        return success
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during installation: {e}")
        return False

def mac_install(env: str = PYMOL_ENV, reqs: str = REQUIREMENTS_FILE) -> bool:
    """
    Performs installation on macOS using pip.

    Args:
        env (str, optional): Path to the PyMOL environment. Defaults to PYMOL_ENV.
        reqs (str, optional): Path to the requirements file. Defaults to REQUIREMENTS_FILE.

    Returns:
        bool: True if installation was successful, False otherwise.
    """
    if not os.path.exists(reqs):
        print(f"Error: Requirements file not found: {reqs}")
        return False
    try:
        requirements_list = get_requirements(reqs)
        ready, packs = check_installed_packages(requirements_list)

        if ready:
            print('Packages already installed.')
            return True

        target_site = sysconfig.get_paths()['purelib']

        print(f"Installing missing packages into {target_site}")
        cmdline = [sys.executable, "-m", "pip", "install",
                   "--upgrade", "--no-warn-script-location",
                   "--target", target_site, *packs]
        result = subprocess.run(cmdline, check=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Output: {result.stdout}")
            return True
        else:
            print(f"Installation failed: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print(f'Error: {e}')
        return False

def linux_install(env: str = LINUX_ENV_FIXED, reqs: str = LINUX_REQS_FIXED) -> bool:
    """
    Performs installation on Linux.

    Args:
        env (str, optional): Path to the PyMOL environment. Defaults to LINUX_ENV_FIXED.
        reqs (str, optional): Path to the requirements file. Defaults to LINUX_REQS_FIXED.

    Returns:
        bool: True if installation was successful, False otherwise.
    """
    if not os.path.exists(reqs):
        print(f"Error: Requirements file not found: {reqs}")
        return False
    try:
        requirements_list = get_requirements(reqs)

        pack_status, missing_packages = check_installed_packages(requirements_list)
        if pack_status:
            print("All packages already installed.")
            return True

        print(f"Missing packages: {missing_packages}")

        if missing_packages:
            print(f"Installing pip packages: {missing_packages}")
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install'] + missing_packages,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    print("Pip packages installed successfully")
                else:
                    print(f"Pip install failed: {result.stderr}")
            except subprocess.CalledProcessError as e:
                print(f"Pip install error: {e}")

        final_status, final_missing = check_installed_packages(requirements_list)

        if final_status:
            print("All packages successfully installed!")
            return True
        print(f"Some packages still missing: {final_missing}")
        return False
    except subprocess.CalledProcessError as e:
        print(f'Error during Linux installation: {e}')
        return False


def register_pymol_functions():
    """
    Register the plugin's core functions as PyMOL commands.

    This function imports the plugin's modular command wrappers and extends
    the PyMOL `cmd` object so that the commands become available to users
    as top-level PyMOL commands.
    """
    # pylint: disable=wrong-import-position, import-outside-toplevel
    from pathlib import Path
    proj_root = Path(__file__).resolve().parents[0]
    sys.path.insert(0, str(proj_root))
    # Plots functions
    from functions.plots.circuit_plot import circuit_plot
    cmd.extend("circuit_plot", circuit_plot)
    from functions.plots.matrix_plot import matrix_plot
    cmd.extend("matrix_plot", matrix_plot)
    from functions.plots.stats_plot import stats_plot
    cmd.extend("stats_plot", stats_plot)
    from functions.plots.matrix_plot_model import matrix_plot_model
    cmd.extend("matrix_plot_model", matrix_plot_model)
    from functions.plots.local_topology_plot import local_topology_plot
    cmd.extend("local_topology_plot", local_topology_plot)

    # Calculating functions
    from functions.calculating.get_cmap import get_cmap
    cmd.extend("get_cmap", get_cmap)
    from functions.calculating.get_matrix import get_matrix
    cmd.extend("get_matrix", get_matrix)
    from functions.calculating.get_stats import get_stats
    cmd.extend("get_stats", get_stats)
    from functions.calculating.energy_cmap import energy_cmap
    cmd.extend("energy_cmap", energy_cmap)
    from functions.calculating.length_filter import length_filter
    cmd.extend("length_filter", length_filter)
    from functions.calculating.local_ct import local_ct
    cmd.extend("local_ct", local_ct)

    # Importing functions
    from functions.importing.retrieve_chain import retrieve_chain
    cmd.extend("retrieve_chain", retrieve_chain)

    # Exporting functions
    from functions.exporting.export_psc import export_psc
    cmd.extend("export_psc", export_psc)
    from functions.exporting.export_cmap3 import export_cmap3
    cmd.extend("export_cmap3", export_cmap3)
    from functions.exporting.export_mat import export_mat
    cmd.extend("export_mat", export_mat)
