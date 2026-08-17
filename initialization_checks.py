"""
Installation and initialization utilities for the Circuit Topology plugin.

This module provides helpers used by the plugin entrypoint to:
- Inspect and parse a conda-style requirements YAML.
- Detect which packages are already available in the current PyMOL
  environment.
- Install missing dependencies into PyMOL's own conda environment.
- Register PyMOL commands that wrap plugin functionality.

Design goals:
- Be robust whether PyMOL is installed system-wide or user-only.
- Install dependencies into the running interpreter's environment (never the
  wrong conda distribution or the wrong environment).
- Provide clear diagnostic output suitable for logging or display in the
  PyMOL terminal.
"""
import importlib.util
import logging
import os
import platform
import subprocess
import sys
from pathlib import Path

from pymol import cmd  # pylint: disable=import-error, no-name-in-module

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Locate the PyMOL installation directory via the official PYMOL_PATH env var.
# Falls back to sys.executable's parent if PYMOL_PATH is not set.
_pymol_path_env = os.environ.get("PYMOL_PATH")
PYMOL_ENV = Path(_pymol_path_env) if _pymol_path_env else Path(sys.executable).parent
# Get directory of env and requirements.yml
PLUGIN_DIR = Path(__file__).parent
REQUIREMENTS_FILE = PLUGIN_DIR / "requirements.yml"
_CONDA_TO_IMPORT = {
    "biopython": "Bio",
    "matplotlib-base": "matplotlib",
    "pyqt": "PyQt5",
    "pyqt5-sip": "PyQt5.sip",
    "qt-main": "PyQt5",
}


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
        return path.resolve().is_relative_to(Path.home().resolve())
    except (OSError, ValueError) as e:
        logger.info("Warning: Could not determine if path is user-accessible: %s", e)
        return False


def is_running_as_admin() -> bool:
    """
    Returns True if the current process has administrator / root privileges.

    On Windows this calls IsUserAnAdmin(); on POSIX it checks effective uid == 0.
    Returns False on any error so callers can treat the result conservatively.
    """
    if platform.system() == "Windows":
        try:
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False
    getuid = getattr(os, "getuid", None)
    return getuid is not None and getuid() == 0


def install_failed(reqs: Path = REQUIREMENTS_FILE) -> None:
    """
    Prints instructions for manual installation of dependencies if automated installation fails.

    Args:
        reqs (Path, optional): Path to the requirements file. Defaults to REQUIREMENTS_FILE.
    """
    try:
        requirements_list = list(requirement_specs(reqs))
    except (FileNotFoundError, ValueError):
        logger.exception("Error reading requirements")
        return

    all_installed, not_installed = check_installed_packages(requirements_list)

    if all_installed:
        logger.info("All packages were installed.")
        return

    if is_path_user(PYMOL_ENV):
        logger.info("PyMOL is in a user directory - no admin permissions needed.")
    else:
        logger.info("PyMOL is in a system directory - admin/root permissions are required to install packages.")

    logger.info("Automated installation failed. The following packages still need to be installed:")
    logger.info("%s", not_installed)

    specs = " ".join(f"conda-forge::{pack}" for pack in not_installed)
    logger.info(
        "To install them, open a system terminal (e.g. Anaconda Prompt) where conda is "
        "available and run the following, then restart PyMOL:",
    )
    logger.info('conda install --yes --prefix "%s" %s', sys.prefix, specs)

    pinned = Path(sys.prefix) / "conda-meta" / "pinned"
    if pinned.is_file():
        logger.info(
            "If conda reports 'InvalidMatchSpec', %s contains a malformed line - the Linux "
            "PyMOL bundle ships 'pymol >=', which conda rejects on every operation in this "
            "environment. Delete that line and retry.", pinned,
        )
    logger.info(
        "If PyMOL is installed system-wide, run that command from an elevated/administrator "
        "terminal, or reinstall PyMOL for your user only.",
    )


def _normalize_requirement_name(requirement: str) -> str | None:
    """Convert a conda-style dependency entry into its package name."""
    requirement = requirement.split("#", maxsplit=1)[0].strip()
    if not requirement or requirement.endswith(":"):
        return None

    if "::" in requirement:
        requirement = requirement.split("::", maxsplit=1)[1]

    if "[" in requirement:
        requirement = requirement.split("[", maxsplit=1)[0]

    for operator in ("==", ">=", "<=", "!=", "~=", "=", ">", "<"):
        if operator in requirement:
            requirement = requirement.split(operator, maxsplit=1)[0]
            break

    requirement = requirement.strip()
    return requirement or None


def requirement_specs(req_path: Path) -> dict[str, str]:
    """
    Parse requirements.yml into package name -> the exact spec the file declares.

    Args:
        req_path (Path): Path to the requirements file.

    Returns:
        dict[str, str]: package name -> spec string, in file order.
    """
    if not req_path.exists():
        msg = f"Requirements file not found: {req_path}"
        raise FileNotFoundError(msg)

    packages: dict[str, str] = {}
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
                        raw = stripped.removeprefix("-").strip()
                        pack = _normalize_requirement_name(raw)
                        if pack and pack not in packages:
                            packages[pack] = raw
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
            True if all installed, False otherwise.
    """
    not_installed = [pack for pack in requirements_list if not _is_package_available(pack)]
    return len(not_installed) == 0, not_installed

def _is_package_available(pack: str) -> bool:
    """Check whether a conda-named package is importable in this interpreter."""
    name = (pack or "").strip()
    if not name:
        return False
    module = _CONDA_TO_IMPORT.get(name.lower(), name)
    try:
        return importlib.util.find_spec(module) is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        try:
            __import__(module)
        except ImportError:
            return False
        else:
            return True


def is_conda_installed() -> tuple[bool, Path | None]:
    """
    Checks if conda is discoverable on the system PATH.

    Returns:
        tuple[bool, Path | None]:
            A tuple containing a boolean (True if found)
            and the path to conda (or None).
    """
    command = "where conda" if platform.system() == "Windows" else "which conda"

    try:
        pipe = subprocess.PIPE
        result = subprocess.run(  # noqa: S602
            command, shell=True, check=True, stdout=pipe, stderr=pipe, text=True,
        )
        first_line = result.stdout.splitlines()[0].strip()
        return True, Path(first_line)
    except (subprocess.CalledProcessError, IndexError):
        return False, None


def _find_conda_executable() -> Path | None:
    """
    Locate the conda executable that owns the running PyMOL environment.

    Returns:
        Path | None: Path to a conda executable, or None if none was found.
    """
    conda_exe = os.environ.get("CONDA_EXE")
    if conda_exe and Path(conda_exe).exists():
        return Path(conda_exe)

    prefix = Path(sys.prefix)
    if platform.system() == "Windows":
        candidates = [prefix / "Scripts" / "conda.exe", prefix / "condabin" / "conda.bat", prefix / "Library" / "bin" / "conda.bat"]
    else:
        candidates = [prefix / "bin" / "conda", prefix / "condabin" / "conda"]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    found, path = is_conda_installed()
    if found and path:
        return path
    return None


def _installed_spec(package: str) -> str | None:
    """
    Pin ``package`` to the version already installed in this prefix, read from conda-meta.

    Args:
        package (str): conda package name, e.g. "pymol".

    Returns:
        str | None: e.g. ``"pymol==3.1.6.1"``, or None if conda has no record of it.
    """
    for record in sorted((Path(sys.prefix) / "conda-meta").glob(f"{package}-*.json")):
        name, version, _build = record.stem.rsplit("-", 2)
        if name == package:
            return f"{package}=={version}"
    return None


def _run_conda(command: list[str]) -> subprocess.CompletedProcess | None:
    """Run a conda command, returning None if it could not be launched at all."""
    try:
        return subprocess.run(command, capture_output=True, text=True, check=False)  # noqa: S603
    except OSError:
        logger.exception("Error occurred while running conda")
        return None


def _retry_without_broken_pins(command: list[str]) -> subprocess.CompletedProcess | None:
    """
    Retry a conda command with a malformed ``conda-meta/pinned`` moved out of the way.

    Returns:
        The retried result, or None if there was no pinned file to move or it could not be moved.
    """
    pinned = Path(sys.prefix) / "conda-meta" / "pinned"
    if not pinned.is_file():
        return None

    moved = pinned.with_suffix(".proteinct-retry")
    logger.warning(
        "Conda rejected %s because it contains a malformed pin. Retrying the install with "
        "that file moved aside temporarily; it will be restored afterwards.", pinned,
    )
    try:
        pinned.replace(moved)
    except OSError:
        logger.exception("Could not move %s aside, so the install cannot be retried", pinned)
        return None

    try:
        return _run_conda(command)
    finally:
        try:
            moved.replace(pinned)
        except OSError:
            logger.exception(
                "Could not restore %s from %s - rename it back by hand to leave PyMOL's "
                "environment exactly as it was.", pinned, moved,
            )


def install_dependencies(reqs: Path = REQUIREMENTS_FILE, missing: list[str] | None = None) -> bool:
    """
    Install plugin dependencies into PyMOL's own conda environment.

    Args:
        reqs (Path, optional): Path to the requirements file. Defaults to REQUIREMENTS_FILE.
        missing (list[str], optional): Install only these packages. Defaults to every requirement.

    Returns:
        bool: True only if conda reports success (exit code 0), False otherwise.
    """
    try:
        specs_by_name = requirement_specs(reqs)
    except (FileNotFoundError, ValueError):
        logger.exception("Could not read the requirements file %s", reqs)
        return False

    conda_exe = _find_conda_executable()
    if conda_exe is None:
        logger.error("Conda executable not found - cannot install dependencies.")
        return False

    wanted = list(specs_by_name) if missing is None else [n for n in missing if n in specs_by_name]
    if not wanted:
        logger.info("No missing dependencies to install.")
        return True

    pins = [spec for spec in (_installed_spec("python"), _installed_spec("pymol")) if spec]
    guards = ["--freeze-installed"]
    if _installed_spec("pymol") is None:
        logger.info("No conda record of pymol to pin; using the classic solver instead.")
        guards.append("--solver=classic")
    if _installed_spec("python") is None:
        pins.append(f"python={sys.version_info.major}.{sys.version_info.minor}")

    specs = [specs_by_name[n] for n in wanted]
    command = [
        str(conda_exe), "install", "--yes", *guards,
        "--prefix", str(sys.prefix), *pins, *specs,
    ]
    logger.info("Installing %s into %s using %s", wanted, sys.prefix, conda_exe)

    result = _run_conda(command)
    if result is None:
        return False

    if result.returncode != 0 and "InvalidMatchSpec" in (result.stderr or ""):
        retried = _retry_without_broken_pins(command)
        if retried is not None:
            result = retried

    if result.stdout:
        logger.info("Installation output: %s", result.stdout)

    if result.returncode != 0:
        logger.error("Installation failed (exit code %s): %s", result.returncode, result.stderr)
        return False

    if result.stderr:
        logger.warning("Installation warnings: %s", result.stderr)
    logger.info("Installation completed successfully.")
    return True


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
    from functions.exporting.export_psx import export_psx
    cmd.extend("export_psx", export_psx)
    from functions.exporting.export_cmap3 import export_cmap3
    cmd.extend("export_cmap3", export_cmap3)
    from functions.exporting.export_mat import export_mat
    cmd.extend("export_mat", export_mat)

    from utils.topology import color_by_topology, get_topology_vector
    cmd.extend("get_topology_vector", get_topology_vector)
    cmd.extend("color_by_topology", color_by_topology)
    from utils.folding_score import get_folding_score
    cmd.extend("get_folding_score", get_folding_score)

