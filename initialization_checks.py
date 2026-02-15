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
import platform
from pymol import cmd  # pylint: disable=import-error, no-name-in-module

# Determine environment and plugin files
pymol_env_path = sys.executable
pymol_env = os.path.dirname(pymol_env_path)
plugin_dir = os.path.dirname(os.path.abspath(__file__))
requirements_file = os.path.join(plugin_dir, "requirements.yml")

# Normalized paths for cross-platform consumption
LINUX_REQS_FIXED = requirements_file.replace("\\", "/")
LINUX_ENV_FIXED = pymol_env.replace("\\", "/")

# PowerShell invocations used on Windows when elevation is required
ADMIN_INIT_CMD = ["powershell.exe", "Start-Process", "powershell.exe",
                  "-ArgumentList", '-ExecutionPolicy Bypass -Command "conda init"',
                  "-Verb", "RunAs"]
USER_INIT_CMD = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-Command", "conda init"]


def is_path_user(path: str) -> bool:
    """
    Determine whether a filesystem path is located under the current user's
    home directory.

    This check is used to infer whether installation can proceed without
    administrative privileges.

    Parameters
    ----------
    path : str
        Path to evaluate.

    Returns
    -------
    bool
        True if the path is in the user's home directory, False otherwise.
    """
    try:
        if not path:
            return False
        path = os.path.abspath(path)
        user_dir = os.path.expanduser("~")

        # Normalize case for Windows
        if platform.system() == "Windows":
            path = path.lower()
            user_dir = user_dir.lower()

        return path.startswith(user_dir)
    except (OSError, ValueError) as e:
        print(f"Warning: Could not determine if path is user-accessible: {e}")
        return False


def pymol_install(env=pymol_env, reqs=requirements_file) -> bool:
    """
    Attempt to install requirements using PyMOL's internal terminal/conda.

    When available, PyMOL exposes a minimal conda environment that can be used
    to perform environment updates. This function uses the PyMOL command API
    to run `conda init` and `conda env update`.

    Parameters
    ----------
    env : str
        Path to the Python environment that PyMOL is using (unused but present
        for API compatibility).
    reqs : str
        Path to the requirements YAML file.

    Returns
    -------
    bool
        True if the installation appears to have succeeded, False otherwise.
    """
    if not os.path.exists(reqs):
        print(f"Error: Requirements file not found: {reqs}")
        return False

    reqs_fixed = reqs.replace("\\", "/")

    print("Using PyMOL terminal with conda to install dependencies...")

    try:
        cmd.do('conda init')
        cmd.do(f"conda env update --file {reqs_fixed}")
        return True
    except Exception as e:
        print(f'Error: {e}')
        return False


def install_failed(reqs=requirements_file) -> None:
    """
    Print clear manual installation instructions in case automated install fails.

    The function parses the requirements file and then prints per-package
    suggested conda commands, with fallbacks for packages that can be installed
    via pip. This supports users in manually completing the installation.
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

    if is_path_user(pymol_env):
        print("Pymol is in user directory - no admin permissions needed.")
    else:
        print("Pymol is in system directory - admin permissions may be needed.")

    print(f'Automated install failed, the following packages need to be installed: {not_installed}')
    print(f'Please note that if PyMOL is installed on the system path admin permission will be required to install packages.')
    print('To install the required packages, please run the following commands in the PyMOL terminal:')

    for pack in not_installed:
        if pack in install_instruc_dict:
            print(install_instruc_dict[pack])
        else:
            print(f'conda install {pack}')

    print('Once all packages are installed, restart PyMOL and reinitialize the plugin.')


def get_requirements(req_path: str):
    """
    Parse a conda-style YAML requirements file and return a list of package
    names required by the plugin.

    The parser is intentionally conservative and focuses on extracting entries
    under the `dependencies` section. It strips common version constraints.

    Parameters
    ----------
    req_path : str
        Path to the requirements YAML file.

    Returns
    -------
    list[str]
        List of package base names (without version specifiers).

    Raises
    ------
    FileNotFoundError
        If the provided path does not exist.
    ValueError
        If there are encoding or parsing errors.
    """
    if not os.path.exists(req_path):
        raise FileNotFoundError(f"Requirements file not found: {req_path}")

    packages = []
    in_dependencies = False
    try:
        with open(req_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                stripped = line.strip()

                if not stripped or stripped.startswith('#'):
                    continue

                if stripped == 'channels:':
                    in_dependencies = False
                    continue
                elif stripped == 'dependencies:':
                    in_dependencies = True
                    continue

                if in_dependencies and stripped.startswith('-'):
                    pack = stripped.replace('- ', '').split('==')[0].split('>=')[0].split('<=')[0]
                    pack = pack.strip()
                    if pack and pack not in packages:
                        packages.append(pack)
    except UnicodeDecodeError as e:
        raise ValueError(f"Unable to read requirements file (encoding issue): {e}")
    except Exception as e:
        raise ValueError(f"Error parsing requirements file at line {line_num}: {e}")

    if not packages:
        print("Warning: No packages found in requirements file")
    return packages


def check_installed_packages(requirements_list):
    """
    Check whether the packages listed are importable in the current Python
    interpreter.

    Parameters
    ----------
    requirements_list : list[str]
        Package names to check.

    Returns
    -------
    tuple
        (all_installed: bool, installed_or_missing: list)
        If all installed then second element is a list of installed packages,
        otherwise it is a list of missing packages.
    """
    import importlib.util

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


def is_conda_installed():
    """
    Check whether `conda` is available on the PATH.

    Returns
    -------
    tuple(bool, str)
        (is_installed, command_output_or_error)
    """
    command = 'where conda' if platform.system() == 'Windows' else 'which conda'

    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, str(e)


def conda_init(user_install: bool) -> bool:
    """
    Initialize conda via PowerShell on Windows.

    This helper runs privileged or non-privileged PowerShell commands to
    execute `conda init` where needed. Returns True when the command returns
    success (exit code 0).
    """
    try:
        if not user_install:
            result = subprocess.run(ADMIN_INIT_CMD, capture_output=True, text=True)
        else:
            result = subprocess.run(USER_INIT_CMD, capture_output=True, text=True)

        print(f'Initialization results output: {result.stdout}')
        if result.stderr:
            print(f'Initialization results error: {result.stderr}')

        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print('Conda initialization timed out')
        return False
    except Exception as e:
        print(f'Error in initialization of conda: {e}')
        return False


def win_install(env=pymol_env, reqs=requirements_file) -> bool:
    """
    Attempt installation on Windows using PowerShell and conda.

    Returns True if installation succeeded.
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
            result = subprocess.run(admin_cmd, capture_output=True, text=True)
        else:
            print("Running installation with user privileges...")
            result = subprocess.run(user_cmd, capture_output=True, text=True)
        print(f"Installation output: {result.stdout}")
        if result.stderr:
            print(f"Installation warnings/errors: {result.stderr}")

        success = result.returncode == 0
        if success:
            print("Installation completed successfully.")
        else:
            print("Installation failed. Please check the output for details.")
        return success
    except Exception as e:
        print(f"Error occurred during installation: {e}")
        return False


def mac_install(env=pymol_env, reqs=requirements_file) -> bool:
    """
    Install missing packages on macOS by using pip to target PyMOL's site-packages.

    This approach avoids modifying the global environment and installs packages
    directly into the directory where PyMOL looks up purelib modules.
    """
    import sysconfig
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
        result = subprocess.run(cmdline, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Output: {result.stdout}")
            return True
        else:
            print(f"Installation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f'Error: {e}')
        return False


def linux_install(env=LINUX_ENV_FIXED, reqs=LINUX_REQS_FIXED) -> bool:
    """
    Attempt installation on Linux platforms.

    The strategy:
    - Use pip for packages that are pip-installable (all except `dssp`).
    - Inform the user that `dssp` requires conda.
    - Accept installations that leave only `dssp` missing for core functionality.
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

        pip_packages = [pkg for pkg in missing_packages if pkg != 'dssp']

        if pip_packages:
            print(f"Installing pip packages: {pip_packages}")
            try:
                result = subprocess.run([sys.executable, '-m', 'pip', 'install'] + pip_packages,
                                        capture_output=True, text=True)
                if result.returncode == 0:
                    print("Pip packages installed successfully")
                else:
                    print(f"Pip install failed: {result.stderr}")
            except Exception as e:
                print(f"Pip install error: {e}")

        if 'dssp' in missing_packages:
            print("Note: DSSP requires conda and may need manual installation")
            print("Run: conda install -c salilab dssp")

        final_status, final_missing = check_installed_packages(requirements_list)
        dssp_only_missing = (len(final_missing) == 1 and 'dssp' in final_missing) if final_missing else False

        if final_status:
            print("All packages successfully installed!")
            return True
        elif dssp_only_missing:
            print("Core packages installed successfully. Only DSSP missing (requires working conda).")
            return True
        elif len(final_missing) <= 1:
            print(f"Installation mostly successful. Only {final_missing} missing.")
            return True
        else:
            print(f"Some packages still missing: {final_missing}")
            return False
    except Exception as e:
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
