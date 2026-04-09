import os
import subprocess
import sys
import platform
from typing import List, Tuple

from pymol import cmd # pylint: disable=import-error, no-name-in-module

# Locate the pymol env
pymol_env_path: str = sys.executable
# Get env path
pymol_env: str = os.path.dirname(pymol_env_path)
# Get directory of env and requirements.yml
plugin_dir: str = os.path.dirname(os.path.abspath(__file__))
requirements_file: str = os.path.join(plugin_dir, "requirements.yml")

LINUX_REQS_FIXED: str = requirements_file.replace("\\", "/")
LINUX_ENV_FIXED: str = pymol_env.replace("\\", "/")

ADMIN_INIT_CMD: List[str] = ["powershell.exe", "Start-Process", "powershell.exe",
                "-ArgumentList", '-ExecutionPolicy Bypass -Command "conda init"',
                "-Verb", "RunAs"]

USER_INIT_CMD: List[str] = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-Command", "conda init"]

def is_path_user(path: str) -> bool:
    """
    Checks if a path is system or user.
    
    Args:
        path: The path to check.
        
    Returns:
        True if the path is in the user's home directory, False otherwise.
    """
    # Finds path origin and compares to the user's home directory
    # If the path is not in the user's home directory, it is on the system path (or another user directory)
    # Either way this will cause failure of install (unless the user is an admin on Mac)
    try:
        if not path:
            return False
        path = os.path.abspath(path)
        user_dir = os.path.expanduser("~")

        # Fixes for case sensitivity in windows
        if platform.system() == "Windows":
            path = path.lower()
            user_dir = user_dir.lower()
        
        # Compares path with user home directory
        # Returns True if it is in the user home directory and false if not
        return path.startswith(user_dir)
    except (OSError, ValueError) as e:
        print(f"Warning: Could not determine if path is user-accessible: {e}")
        return False

def pymol_install(env: str = pymol_env, reqs: str = requirements_file) -> bool:
    """
    Tries install with pymol terminal.
    
    Args:
        env: The environment path.
        reqs: The requirements file path.
        
    Returns:
        True if the install was successful, False otherwise.
    """
    # Fixes the path so that PyMOL doesn't get confused
    if not os.path.exists(reqs):
        print(f"Error: Requirements file not found: {reqs}")
        return False

    reqs_fixed = reqs.replace("\\", "/")

    print("Using PyMOL terminal with conda to install dependencies...")     

    # Trys to install
    try:   
        cmd.do('conda init')
        cmd.do(f"conda env update --file {reqs_fixed}")
        return True
    # Returns False if an error occurs
    # Return True if the run was successful
    except Exception as e:
        print(f'Error: {e}')
        return False

def install_failed(reqs: str = requirements_file) -> None:
    """
    Give instructions on how to install dependencies if installation fails.
    
    Args:
        reqs: The requirements file path.
    """
    # Instructions for install
    # Made manually and needs to be updated if new packages are added
    install_instruc_dict = {
        'pandas': 'conda install conda-forge::pandas',
        'dssp': 'conda install salilab::dssp',
        'scipy': 'conda install conda-forge::scipy',
        'ipywidgets': 'conda install conda-forge::ipywidgets',
        'matplotlib': 'conda install conda-forge::matplotlib',
    }

    try:
        requirements_list = get_requirements(reqs)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error reading requirements: {e}")
        return

    # Get the missing packages (if any)
    all_installed, not_installed = check_installed_packages(requirements_list)

    # If they were already all installed then nothing needs to be done
    if all_installed:
        print('All packages were installed.')
        return
    # Otherwise give instructions
    if is_path_user(pymol_env):
        print("Pymol is in user directory - no admin permissions needed.")
    else:
        print("Pymol is in system directory - admin permissions may be needed.")
        
    print(f'Automated installed failed, the following packages need to be installed: {not_installed}')

    print('Please note that if PyMOL is installed on the system path admin permission will be required to install packages.')

    print('To install the required packages, please run the following commands in the PyMOL terminal:')
    for pack in not_installed:
        if pack in install_instruc_dict:
            print(install_instruc_dict[pack])
        else:
            print(f'conda install {pack}')
    
    print('Once all packages are installed, restart PyMOL and reinitialize the plugin.')

def get_requirements(req_path: str) -> List[str]:
    """
    Gets the required packages from the yml file.
    
    Args:
        req_path: The path to the requirements file.
        
    Returns:
        A list of required packages.
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

def check_installed_packages(requirements_list: List[str]) -> Tuple[bool, List[str]]:
    """
    Checks to see if the necessary packages are installed.
    
    Args:
        requirements_list: A list of required packages.
        
    Returns:
        A tuple containing a boolean indicating if all packages are installed and a list of missing packages.
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

def is_conda_installed() -> Tuple[bool, str]:
    """
    Checks to see if conda is installed on the system.
    
    Returns:
        A tuple containing a boolean indicating if conda is installed and the path to conda.
    """
    command = 'where conda' if platform.system()=='Windows' else 'which conda'

    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return True, result.stdout
    
    except subprocess.CalledProcessError as e:
        return False, str(e)

def conda_init(user_install: bool) -> bool:
    """
    Initializes conda in powershell.
    
    Args:
        user_install: A boolean indicating if the install is for the user.
        
    Returns:
        True if the initialization was successful, False otherwise.
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
        print(f'Error in intialization of conda: {e}')
        return False

def win_install(env: str = pymol_env, reqs: str = requirements_file) -> bool:
    """
    Windows install.
    
    Args:
        env: The environment path.
        reqs: The requirements file path.
        
    Returns:
        True if the install was successful, False otherwise.
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

def mac_install(env: str = pymol_env, reqs: str = requirements_file) -> bool:
    """
    Mac install.
    
    Args:
        env: The environment path.
        reqs: The requirements file path.
        
    Returns:
        True if the install was successful, False otherwise.
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

        # Absolute path to the directory where PyMOL keeps packages
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

def linux_install(env: str = LINUX_ENV_FIXED, reqs: str = LINUX_REQS_FIXED) -> bool:
    """
    Linux install.
    
    Args:
        env: The environment path.
        reqs: The requirements file path.
        
    Returns:
        True if the install was successful, False otherwise.
    """
    if not os.path.exists(reqs):
        print(f"Error: Requirements file not found: {reqs}")
        return False
    try:
        requirements_list = get_requirements(reqs)
        
        # Check if packages are already installed
        pack_status, missing_packages = check_installed_packages(requirements_list)
        if pack_status:
            print("All packages already installed.")
            return True
        
        print(f"Missing packages: {missing_packages}")
        
        # Separate pip and conda packages
        pip_packages = [pkg for pkg in missing_packages if pkg != 'dssp']
        
        # Install pip packages first (these work reliably)
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
        # Since we dont need dssp for core functionality, accept if only dssp is missing
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

def register_pymol_functions() -> None:
    """Register functions as PyMOL commands."""

    # Plots functions
    from .functions.plots.circuit_plot import circuit_plot
    cmd.extend("circuit_plot", circuit_plot)
    from .functions.plots.matrix_plot import matrix_plot
    cmd.extend("matrix_plot", matrix_plot)
    from .functions.plots.stats_plot import stats_plot
    cmd.extend("stats_plot", stats_plot)
    from .functions.plots.matrix_plot_model import matrix_plot_model
    cmd.extend("matrix_plot_model", matrix_plot_model)
    from .functions.plots.local_topology_plot import local_topology_plot
    cmd.extend("local_topology_plot", local_topology_plot)

    # Calculating functions
    from .functions.calculating.get_cmap import get_cmap
    cmd.extend("get_cmap", get_cmap)
    from .functions.calculating.get_matrix import get_matrix
    cmd.extend("get_matrix", get_matrix)
    from .functions.calculating.get_stats import get_stats
    cmd.extend("get_stats", get_stats)
    from .functions.calculating.energy_cmap import energy_cmap
    cmd.extend("energy_cmap", energy_cmap)
    from .functions.calculating.string_pdb import string_pdb
    cmd.extend("string_pdb", string_pdb)
    from .functions.calculating.secondary_struc_cmap import secondary_struc_cmap
    cmd.extend("secondary_struc_cmap", secondary_struc_cmap)
    from .functions.calculating.secondary_struc_filter import secondary_struc_filter
    cmd.extend("secondary_struc_filter", secondary_struc_filter)
    from .functions.calculating.glob_score import glob_score
    cmd.extend("glob_score", glob_score)
    from .functions.calculating.length_filter import length_filter
    cmd.extend("length_filter", length_filter)
    from .functions.calculating.contact_order import contact_order
    cmd.extend("contact_order", contact_order)
    from .functions.calculating.local_ct import local_ct
    cmd.extend("local_ct", local_ct)

    # Importing functions
    from .functions.importing.retrieve_chain import retrieve_chain
    cmd.extend("retrieve_chain", retrieve_chain)
    from .functions.importing.retrieve_cif import retrieve_cif
    cmd.extend("retrieve_cif", retrieve_cif)
    from .functions.importing.retrieve_cif_list import retrieve_cif_list
    cmd.extend("retrieve_cif_list", retrieve_cif_list)
    from .functions.importing.retrieve_secondary_struc import retrieve_secondary_struc
    cmd.extend("retrieve_secondary_struc", retrieve_secondary_struc)
    from .functions.importing.stride_secondary_struc import stride_secondary_struc
    cmd.extend("stride_secondary_struc", stride_secondary_struc)

    # Exporting functions
    from .functions.exporting.export_psc import export_psc
    cmd.extend("export_psc", export_psc)
    from .functions.exporting.export_cmap3 import export_cmap3
    cmd.extend("export_cmap3", export_cmap3)
    from .functions.exporting.export_mat import export_mat
    cmd.extend("export_mat", export_mat)
    from .functions.exporting.export_cmap4 import export_cmap4
    cmd.extend("export_cmap4", export_cmap4)
    from .functions.exporting.export_circuit import export_circuit
    cmd.extend("export_circuit", export_circuit)
