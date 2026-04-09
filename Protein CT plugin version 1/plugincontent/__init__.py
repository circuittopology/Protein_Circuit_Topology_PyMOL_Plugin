import os
import sys
import platform
from typing import Optional

from pymol.plugins import addmenuitemqt  # pylint: disable=import-error, no-name-in-module

from .initialization_checks import *

# Locate the pymol env
pymol_env_path = sys.executable
# Get env path
pymol_env = os.path.dirname(pymol_env_path)
# Get directory of env and requirements.yml
plugin_dir = os.path.dirname(os.path.abspath(__file__))
requirements_file = os.path.join(plugin_dir, "requirements.yml")

def __init_plugin__(app: Optional[object] = None) -> None:
    """
    Initializes the Protein Circuit Topology plugin.
    
    Args:
        app: Optional application object passed by PyMOL.
    """
    # Print statements
    print("Beginning ProteinCT plugin initialization")

    auto_install = True
    
    if auto_install == False:
        try:
            print('Checking ProteinCT plugin initialization')
            register_pymol_functions()

            addmenuitemqt('Protein Circuit Topology Plugin', run_plugin_gui)
            
            print('ProteinCT plugin initialized')
            return
        except Exception:
            install_failed(reqs=requirements_file)
            return
    
    # Determine what needs to be installed
    requirements_list = get_requirements(req_path=requirements_file)
    pack_status, packs = check_installed_packages(requirements_list)

    # Get the user's system type
    sys_type = platform.system()

    # Check if pymol is on the system or user path
    pymol_path_user = is_path_user(pymol_env)

    # If not on mac and Pymol is on system path, then install will fail
    if not pymol_path_user and sys_type != "Darwin":
        print('PyMOL has been installed on the system environment path, automated plugin install cannot occur for ProteinCT plugin.')
        install_failed(reqs=requirements_file)
        return
    # If on mac and pymol is on system path, if the user is an admin install should be successful so it will continue
    if not pymol_path_user and sys_type == "Darwin":
        print("PyMOL has been installed on the system path, automated install will still be attempted.")
        print("Assuming the user is an admin, automated install should succeed.")

    # Check if plugin already initialized before attempting install
    try: 
        print('Checking ProteinCT plugin initialization')
        register_pymol_functions()

        addmenuitemqt('Protein Circuit Topology Plugin', run_plugin_gui)

        print('ProteinCT plugin initialized')
        return

    except Exception as e:
        print(f'Error: {e}')

        print(f"The following packages need to be installed for ProteinCT plugin: {packs}")
        
        # Try pymol terminal install first always
        result = pymol_install()

        if result:
            try: 
                print('Checking ProteinCT plugin initialization')
                register_pymol_functions()

                addmenuitemqt('Protein Circuit Topology Plugin', run_plugin_gui)
                
                print('ProteinCT plugin initialized')
                return
            except Exception as e:
                print(f"Error: {e}")

    try:
        print('Checking ProteinCT plugin initialization')
        register_pymol_functions()

        addmenuitemqt('Protein Circuit Topology Plugin', run_plugin_gui)
        
        print('ProteinCT plugin initialized')
        return
    # If pymol install fails try system specific install methods
    except Exception:
        if sys_type == "Windows":
            result = win_install()

            if result == True:
                try: 
                    print('Checking ProteinCT plugin initialization')
                    register_pymol_functions()

                    addmenuitemqt('Protein Circuit Topology Plugin', run_plugin_gui)
                    
                    print('ProteinCT plugin initialized')
                    return
                except Exception as e:
                    print(f"Error: {e}")
                    install_failed()
                    return
                
        elif sys_type == "Darwin":
            result = mac_install()

            if result == True:
                try: 
                    print('Checking ProteinCT plugin initialization')
                    register_pymol_functions()

                    addmenuitemqt('Protein Circuit Topology Plugin', run_plugin_gui)
                    
                    print('ProteinCT plugin initialized')
                    return
                except Exception as e:
                    print(f"Error: {e}")
                    install_failed()
                    return
        else:
            result = linux_install()
            
            if result == True:
                try: 
                    print('Checking ProteinCT plugin initialization')
                    register_pymol_functions()

                    addmenuitemqt('Protein Circuit Topology Plugin', run_plugin_gui)
                    
                    print('ProteinCT plugin initialized')
                    return
                
                except Exception as e:
                    print(f"Error: {e}")
                    install_failed()
                    return


dialog_instance = None


def run_plugin_gui() -> object:
    """
    Runs the Protein Circuit Topology Plugin GUI.
    
    Returns:
        The dialog instance of the plugin GUI.
    """
    from .gui_class import CTDialog
    global dialog_instance
    if dialog_instance is None or not dialog_instance.isVisible():
        dialog_instance = CTDialog()
        dialog_instance.show()
    else:
        dialog_instance.raise_()
        dialog_instance.activateWindow()

    return dialog_instance
