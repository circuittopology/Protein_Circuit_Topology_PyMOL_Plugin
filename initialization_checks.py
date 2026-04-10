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
import importlib.util
import logging
import os
import platform
import subprocess
import sys
import sysconfig
from pathlib import Path

from pymol import cmd  # pylint: disable=import-error, no-name-in-module

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Locate the pymol env
PYMOL_ENV_PATH = sys.executable
# Get env path
PYMOL_ENV = Path(PYMOL_ENV_PATH).parent
# Get directory of env and requirements.yml
PLUGIN_DIR = Path(__file__).parent
REQUIREMENTS_FILE = PLUGIN_DIR / "requirements.yml"

LINUX_REQS_FIXED = str(REQUIREMENTS_FILE).replace("\\", "/")
LINUX_ENV_FIXED = str(PYMOL_ENV).replace("\\", "/")

ADMIN_INIT_CMD = ["powershell.exe", "Start-Process", "powershell.exe",
                "-ArgumentList", '-ExecutionPolicy Bypass -Command "conda init"',
                "-Verb", "RunAs"]

USER_INIT_CMD = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-Command", "conda init"]

def is_path_user(path: Path | None) -> bool:
    """
    Checks if a given path is within the user's home directory.

    Args:
        path (Path | None): The path to check.

    Returns:
        bool: True if the path is within the user's home directory, False otherwise.
    """
    try:
        if not path:
            return False
        path = path.resolve()
        user_dir = Path.home()

        return str(path).startswith(str(user_dir))
    except (OSError, ValueError) as e:
        logger.info("Warning: Could not determine if path is user-accessible: %s", e)
        return False

def pymol_install(env: Path = PYMOL_ENV, reqs: Path = REQUIREMENTS_FILE) -> bool:
    """
    Attempts to install dependencies using the PyMOL terminal and conda.

    Args:
        env (Path, optional): Path to the PyMOL environment. Defaults to PYMOL_ENV.
        reqs (Path, optional): Path to the requirements file. Defaults to REQUIREMENTS_FILE.

    Returns:
        bool: True if the install commands were issued, False on error.
    """
    if not reqs.exists():
        logger.error("Error: Requirements file not found: %s", reqs)
        return False

    reqs_fixed = str(reqs).replace("\\", "/")

    logger.info("Using PyMOL terminal with conda to install dependencies...")

    cmd.do("conda init")
    cmd.do(f"conda env update --file {reqs_fixed}")
    return True

def install_failed(reqs: Path = REQUIREMENTS_FILE) -> None:
    """
    Prints instructions for manual installation of dependencies if automated installation fails.

    Args:
        reqs (Path, optional): Path to the requirements file. Defaults to REQUIREMENTS_FILE.
    """
    install_instruc_dict = {
        "pandas": "conda install conda-forge::pandas",
        "matplotlib": "conda install conda-forge::matplotlib",
    }

    try:
        requirements_list = get_requirements(reqs)
    except (FileNotFoundError, ValueError):
        logger.exception("Error reading requirements")
        return

    all_installed, not_installed = check_installed_packages(requirements_list)

    if all_installed:
        logger.info("All packages were installed.")
        return

    if is_path_user(PYMOL_ENV):
        logger.info("Pymol is in user directory - no admin permissions needed.")
    else:
        logger.info("Pymol is in system directory - admin permissions may be needed.")

    logger.info("Automated installation failed, the following packages need to be installed")
    logger.info("%s", not_installed)
    logger.info("""Please note that if PyMOL is installed on the system path, then
          admin permission will be required to install packages.
          To install the required packages, run the following commands in the PyMOL terminal:""")

    for pack in not_installed:
        if pack in install_instruc_dict:
            logger.info(install_instruc_dict[pack])
        else:
            logger.info("conda install %s", pack)

    logger.info("Once all packages are installed, restart PyMOL and reinitialize the plugin.")

def get_requirements(req_path: Path) -> list[str]:
    """
    Parses the requirements.yml file to get a list of required packages.

    Args:
        req_path (Path): Path to the requirements file.

    Returns:
        list[str]: A list of package names.
    """
    if not req_path.exists():
        msg = f"Requirements file not found: {req_path}"
        raise FileNotFoundError(msg)

    packages = []
    in_dependencies = False
    try:
        with req_path.open(mode="r", encoding="utf-8") as file:
            for line_num, line in enumerate(file, 1):
                try:
                    stripped = line.strip()

                    if not stripped or stripped.startswith("#"):
                        continue

                    if stripped == "channels:":
                        in_dependencies = False
                        continue

                    if stripped == "dependencies:":
                        in_dependencies = True
                        continue

                    if in_dependencies and stripped.startswith("-"):
                        pack = stripped.replace("- ", "")
                        pack = pack.split("==")[0].split(">=")[0].split("<=")[0]
                        pack = pack.strip()
                        if pack and pack not in packages:
                            packages.append(pack)
                except Exception as e:
                    msg_0 = f"Error parsing requirements file at line {line_num}: {e}"
                    raise ValueError(msg_0) from e
    except UnicodeDecodeError as e:
        msg_1 = f"Unable to read requirements file (encoding issue): {e}"
        raise ValueError(msg_1) from e

    if not packages:
        logger.warning("No packages found in requirements file")
    return packages


def check_installed_packages(requirements_list: list[str]) -> tuple[bool, list[str]]:
    """
    Checks if the required packages are installed in the current environment.

    Args:
        requirements_list (list[str]): List of package names to check.

    Returns:
        tuple[bool, list[str]]:
            True if all installed, False otherwise,
            and a list of packages (missing if False, installed if True).
    """
    not_installed = []
    installed = []

    try:
        for pack in requirements_list:
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


def is_conda_installed() -> tuple[bool, Path | None]:
    """
    Checks if conda is installed on the system.

    Returns:
        tuple[bool, Path | None]:
            A tuple containing a boolean (True if installed) 
            and the path to conda (or error message).
    """
    command = "where conda" if platform.system() == "Windows" else "which conda"

    try:
        pipe = subprocess.PIPE
        result = subprocess.run(
            command, shell=True, check=True, stdout=pipe, stderr=pipe, text=True
        )
        return True, Path(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        return False, None


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

        logger.info("Initialization results output: %s", result.stdout)
        if result.stderr:
            logger.error("Initialization results error: %s", result.stderr)

        return result.returncode == 0
    except subprocess.TimeoutExpired:
        logger.exception("Conda initialization timed out")
        return False
    except OSError as e:
        logger.exception("Error in initialization of conda: %s", e)
        return False

def win_install(env: Path = PYMOL_ENV, reqs: Path = REQUIREMENTS_FILE) -> bool:
    """
    Performs installation on Windows using PowerShell and conda.

    Args:
        env (Path, optional): Path to the PyMOL environment. Defaults to PYMOL_ENV.
        reqs (Path, optional): Path to the requirements file. Defaults to REQUIREMENTS_FILE.

    Returns:
        bool: True if installation was successful, False otherwise.
    """
    if not reqs.exists():
        logger.error("Error: Requirements file not found: %s", reqs)
        return False

    conda_installed, path = is_conda_installed()
    if not conda_installed:
        logger.error("Error: Conda not found on system")
        return False
    conda_path = path or None
    conda_user_path = is_path_user(conda_path)
    conda_initialized = conda_init(user_install=conda_user_path)

    if not conda_initialized:
        return False

    reqs_fixed = str(reqs).replace("\\", "/")
    win_cmds = f'conda env update --file "{reqs_fixed}"'

    admin_cmd = ["powershell.exe", "Start-Process", "powershell.exe",
                 "-ArgumentList", f'-ExecutionPolicy Bypass -Command "{win_cmds}"',
                 "-Verb", "RunAs", "-Wait"]
    user_cmd = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-Command", win_cmds]
    try:
        if not conda_user_path:
            logger.info("Running installation with admin privileges...")
            result = subprocess.run(admin_cmd, check=True, capture_output=True, text=True)
        else:
            logger.info("Running installation with user privileges...")
            result = subprocess.run(user_cmd, check=True, capture_output=True, text=True)
        logger.info("Installation output: %s", result.stdout)
        if result.stderr:
            logger.warning("Installation warnings/errors: %s", result.stderr)

        success = result.returncode == 0
        if success:
            logger.info("Installation completed successfully.")
        else:
            logger.error("Installation failed. Please check the output for details.")
        return success
    except subprocess.CalledProcessError as e:
        logger.exception("Error occurred during installation: %s", e)
        return False

def mac_install(env: Path = PYMOL_ENV, reqs: Path = REQUIREMENTS_FILE) -> bool:
    """
    Performs installation on macOS using pip.

    Args:
        env (Path, optional): Path to the PyMOL environment. Defaults to PYMOL_ENV.
        reqs (Path, optional): Path to the requirements file. Defaults to REQUIREMENTS_FILE.

    Returns:
        bool: True if installation was successful, False otherwise.
    """
    if not reqs.exists():
        logger.error("Error: Requirements file not found: %s", reqs)
        return False
    try:
        requirements_list = get_requirements(reqs)
        ready, packs = check_installed_packages(requirements_list)

        if ready:
            logger.info("Packages already installed.")
            return True

        target_site = sysconfig.get_paths()["purelib"]

        logger.info("Installing missing packages into %s", target_site)
        cmdline = [sys.executable, "-m", "pip", "install",
                   "--upgrade", "--no-warn-script-location",
                   "--target", target_site, *packs]
        result = subprocess.run(cmdline, check=True, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("Output: %s", result.stdout)
            return True
        else:
            logger.error("Installation failed: %s", result.stderr)
            return False
    except subprocess.CalledProcessError as e:
        logger.exception("Error occurred during installation: %s", e)
        return False

def linux_install(env: Path = LINUX_ENV_FIXED, reqs: Path = LINUX_REQS_FIXED) -> bool:
    """
    Performs installation on Linux.

    Args:
        env (Path, optional): Path to the PyMOL environment. Defaults to LINUX_ENV_FIXED.
        reqs (Path, optional): Path to the requirements file. Defaults to LINUX_REQS_FIXED.

    Returns:
        bool: True if installation was successful, False otherwise.
    """
    if not reqs.exists():
        logger.error("Error: Requirements file not found: %s", reqs)
        return False
    try:
        requirements_list = get_requirements(reqs)

        pack_status, missing_packages = check_installed_packages(requirements_list)
        if pack_status:
            logger.info("All packages already installed.")
            return True

        logger.info("Missing packages: %s", missing_packages)

        if missing_packages:
            logger.info("Installing pip packages: %s", missing_packages)
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", *missing_packages],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    logger.info("Pip packages installed successfully")
                else:
                    logger.error("Pip install failed: %s", result.stderr)
            except subprocess.CalledProcessError as e:
                logger.exception("Pip install error: %s", e)

        final_status, final_missing = check_installed_packages(requirements_list)

        if final_status:
            logger.info("All packages successfully installed!")
            return True
        logger.error("Some packages still missing: %s", final_missing)
        return False
    except subprocess.CalledProcessError as e:
        logger.exception("Error during Linux installation: %s", e)
        return False


def register_pymol_functions():
    """
    Register the plugin's core functions as PyMOL commands.

    This function imports the plugin's modular command wrappers and extends
    the PyMOL `cmd` object so that the commands become available to users
    as top-level PyMOL commands.
    """
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
