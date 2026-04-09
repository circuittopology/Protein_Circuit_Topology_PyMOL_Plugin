# Protein Circuit Topology Plugin - Complete API Documentation

This document reflects the **current source tree** and lists callable entry points by module category.

**Total Callable Entry Points:** 112
**Python Files With Callables:** 37

## Table of Contents

1. [Calculating Functions](#calculating-functions) (6 functions)
2. [Plotting Functions](#plotting-functions) (6 functions)
3. [Importing Functions](#importing-functions) (1 functions)
4. [Exporting Functions](#exporting-functions) (3 functions)
5. [Analysis Functions](#analysis-functions) (6 functions)
6. [Utility Functions](#utility-functions) (36 functions)
7. [GUI Functions](#gui-functions) (43 functions)
8. [Initialization Functions](#initialization-functions) (11 functions)

## Calculating Functions

### `energy_cmap(index, numbering, res_names, protid, potential_sign='-')`

**Module:** `functions/calculating/energy_cmap.py`

Applies an energy filter on an existing Residue contact map.

### `get_cmap(chain, level='chain', cutoff_distance=4.5, cutoff_numcontacts=5, exclude_neighbour=3)`

**Module:** `functions/calculating/get_cmap.py`

Creates a residue-residue contact map for a given chain or model.

### `get_matrix(index, protid)`

**Module:** `functions/calculating/get_matrix.py`

Creates a topological relationship matrix for a Residue contact map.

### `get_stats(mat)`

**Module:** `functions/calculating/get_stats.py`

Calculates the percentage of entangled contacts further along the diagonal.

### `length_filter(index, distance, mode='<')`

**Module:** `functions/calculating/length_filter.py`

Applies a length filter to an existing residue contact map index.

### `local_ct(index, mat, numbering)`

**Module:** `functions/calculating/local_ct.py`

Calculates the local circuit topology parameters.

## Plotting Functions

### `circuit_plot(index, protid, numbering)`

**Module:** `functions/plots/circuit_plot.py`

Creates a residue contact map plot.

### `local_topology_plot(index, mat, numbering, protid, siteid, relation)`

**Module:** `functions/plots/local_topology_plot.py`

Generates plots for local topology showing specific contact relationships.

### `matrix_plot(mat, protid)`

**Module:** `functions/plots/matrix_plot.py`

Creates a topological relations matrix plot for a single chain.

### `matrix_plot_model(mat, protid)`

**Module:** `functions/plots/matrix_plot_model.py`

Creates a topological relations matrix plot for a whole model.

### `autopct_funct(pct)`

**Module:** `functions/plots/stats_plot.py`

Format string for pie chart percentages.

### `stats_plot(entangled, psc, protid)`

**Module:** `functions/plots/stats_plot.py`

Plots the amount of psc and entangled contacts.

## Importing Functions

### `retrieve_chain(input_file, chainid=0)`

**Module:** `functions/importing/retrieve_chain.py`

Retrieves a Chain object from a PDB or CIF file.

## Exporting Functions

### `export_cmap3(index, protid, numbering, output_dir)`

**Module:** `functions/exporting/export_cmap3.py`

Transforms Residue contact map indices to a contact map and exports it to a csv file.

### `export_mat(index, mat, protid, output_dir)`

**Module:** `functions/exporting/export_mat.py`

Exports a topological relations matrix to a csv.

### `export_psc(psclist, output_dir)`

**Module:** `functions/exporting/export_psc.py`

Exports amount of PSC contacts to a csv file.

## Analysis Functions

### `run_local_ct(self)`

**Module:** `analysis/local_ct_analysis.py`

Runs the local circuit topology analysis.

### `run_multi_analysis(self)`

**Module:** `analysis/multiple_file_analysis.py`

Runs analysis across multiple files or trajectory frames.

### `run_standard_analysis(self)`

**Module:** `analysis/single_file_analysis.py`

Runs the standard circuit topology analysis for a single file.

### `run_single_frame_analysis(self)`

**Module:** `analysis/single_frame_analysis.py`

Runs analysis for a single frame of a trajectory.

### `toggle_frame_controls(self, enabled)`

**Module:** `analysis/single_frame_analysis.py`

Enables or disables single frame analysis controls.

### `visualize_molecule(self, contact_type)`

**Module:** `analysis/visualization.py`

Visualizes the topology on the molecule inside PyMOL.

## Utility Functions

### `clear_selected_local_file(self)`

**Module:** `utils/clear_file.py`

Clears the selected local file from PyMOL and UI.

### `clear_selected_single_file(self)`

**Module:** `utils/clear_file.py`

Clears the selected single file from PyMOL and UI.

### `choose_file(self)`

**Module:** `utils/directory.py`

Opens a file dialog to select an input structure file.

### `choose_input_dir_multi(self)`

**Module:** `utils/directory.py`

Opens a dialog to choose a multi-file input directory.

### `choose_local_file(self)`

**Module:** `utils/directory.py`

Opens a file dialog to select a local input structure file.

### `choose_local_output_dir(self)`

**Module:** `utils/directory.py`

Opens a dialog to choose a local output directory.

### `choose_output_dir(self)`

**Module:** `utils/directory.py`

Opens a dialog to choose an output directory.

### `choose_output_dir_multi(self)`

**Module:** `utils/directory.py`

Opens a dialog to choose a multi-file output directory.

### `set_label_text_elided(file_path, label)`

**Module:** `utils/directory.py`

Sets elided text on a QLabel.

### `get_folding_score(mat, index, numbering)`

**Module:** `utils/folding_score.py`

Calculate the folding score based on the given relations, using topology data.

### `get_local_values(self)`

**Module:** `utils/get_values.py`

Retrieves values from the local CT analysis GUI elements.

### `get_multiple_values(self)`

**Module:** `utils/get_values.py`

Retrieves values from the multi-file analysis GUI elements.

### `get_values(self)`

**Module:** `utils/get_values.py`

Retrieves values from the standard analysis GUI elements.

### `get_vis_vals(self)`

**Module:** `utils/get_values.py`

Retrieves values from the visualization GUI elements.

### `init_timers(self)`

**Module:** `utils/helpers.py`

Initializes timers for updating lists.

### `make_info_button(tooltip)`

**Module:** `utils/helpers.py`

Creates an info button with a tooltip.

### `object_exists(name)`

**Module:** `utils/helpers.py`

Checks if a given object name exists in PyMOL.

### `update_chain_combo_box(self)`

**Module:** `utils/helpers.py`

Updates the chain combo box with current chain residues.

### `has_non_polymer_atoms()`

**Module:** `utils/non_polymer.py`

Checks if there are any non-polymer atoms in PyMOL.

### `new_file_has_non_polymer_atoms(obj_name)`

**Module:** `utils/non_polymer.py`

Checks if a newly loaded file has non-polymer atoms.

### `remove_non_polymer_atoms()`

**Module:** `utils/non_polymer.py`

Removes non-polymer atoms from all objects in PyMOL.

### `show_warning_dialog(self)`

**Module:** `utils/non_polymer.py`

Shows a warning dialog before removing non-polymer atoms.

### `handle_local_object_change(self, obj_name)`

**Module:** `utils/object_change.py`

Handles changes in the selected local object.

### `handle_standard_object_change(self, obj_name)`

**Module:** `utils/object_change.py`

Handles changes in the selected standard object.

### `get_residue_range(self, obj_name)`

**Module:** `utils/residues.py`

Gets the residue range for a specific object.

### `update_residue_range(self)`

**Module:** `utils/residues.py`

Updates the UI residue range based on the selected chain.

### `color_by_topology(molecule_name, topology_vector, numbering, topology_type)`

**Module:** `utils/topology.py`

Function that takes the topology vector from the get_topology_vector function and

### `get_topology_vector(mat, index, topology_type, numbering)`

**Module:** `utils/topology.py`

The get_topology_vector that Vasiliy provided that we modified to take the actual contact values

### `export_frames_from_traj(self)`

**Module:** `utils/trajectory.py`

Converts a loaded structure and trajectory into a directory of PDB frames.

### `select_mol_file(self)`

**Module:** `utils/trajectory.py`

Opens a file dialog to select a structure file (PDB/CIF) and loads it into PyMOL.

### `select_xtc_file(self)`

**Module:** `utils/trajectory.py`

Opens a file dialog to select a trajectory file and loads it into PyMOL.

### `update_list(self)`

**Module:** `utils/updates.py`

Updates the list of objects from PyMOL.

### `update_local_list(self)`

**Module:** `utils/updates.py`

Updates the list of local objects from PyMOL.

### `update_output_widgets(self)`

**Module:** `utils/updates.py`

Updates the visibility of standard analysis output widgets based on checkboxes.

### `update_output_widgets_local(self)`

**Module:** `utils/updates.py`

Updates the visibility of local CT output widgets based on checkboxes.

### `update_output_widgets_multi(self)`

**Module:** `utils/updates.py`

Updates the visibility of multi-file output widgets based on checkboxes.

## GUI Functions

### `__init_plugin__(app=None)`

**Module:** `__init__.py`

Initializes the Protein Circuit Topology plugin.

### `run_plugin_gui()`

**Module:** `__init__.py`

Runs the Protein Circuit Topology Plugin GUI.

### `__init__(self, parent=None)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Initializes the CTDialog instance.

### `choose_file(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Opens a dialog to choose a file.

### `choose_input_dir_multi(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Opens a dialog to choose a multiple input directory.

### `choose_local_file(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Opens a dialog to choose a local file.

### `choose_local_output_dir(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Opens a dialog to choose a local output directory.

### `choose_output_dir(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Opens a dialog to choose an output directory.

### `choose_output_dir_multi(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Opens a dialog to choose a multiple output directory.

### `clear_selected_local_file(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Clears the currently selected local file.

### `clear_selected_single_file(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Clears the currently selected single file.

### `export_frames_from_traj(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Exports frames from a trajectory.

### `get_local_values(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Retrieves and processes local values.

### `get_multiple_values(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Retrieves and processes multiple values.

### `get_residue_range(self, obj_name=None)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Gets the residue range for the selected object.

### `get_values(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Retrieves and processes standard values.

### `get_vis_vals(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Retrieves visualization values.

### `handle_local_object_change(self, obj_name=None)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Handles changes in the selected local object.

### `handle_standard_object_change(self, obj_name=None)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Handles changes in the selected standard object.

### `init_local_tab(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Initializes the local tab UI.

### `init_multi_file_tab(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Initializes the multi-file tab UI.

### `init_single_file_tab(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Initializes the single file tab UI.

### `init_timers(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Initializes application timers.

### `init_ui(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Sets up the initial user interface elements.

### `run_local_ct(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Runs the local circuit topology analysis.

### `run_multi_analysis(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Runs multiple file analysis.

### `run_single_frame_analysis(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Runs the single frame analysis.

### `run_standard_analysis(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Runs the standard circuit topology analysis.

### `select_mol_file(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Selects a molecule file.

### `select_xtc_file(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Selects an XTC trajectory file.

### `show_warning_dialog(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Shows a warning dialog for non-polymer selections.

### `toggle_frame_controls(self, enabled)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Toggles frame controls.

### `update_chain_combo_box(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Updates the chain combo box choices.

### `update_list(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Updates the general list.

### `update_local_list(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Updates the local list.

### `update_output_widgets(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Updates general output widgets.

### `update_output_widgets_local(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Updates local output widgets.

### `update_output_widgets_multi(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Updates multi-file output widgets.

### `update_residue_range(self)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Updates the displayed residue range.

### `visualize_molecule(self, contact_type)`

**Module:** `gui_class.py`

**Type:** `CTDialog` method

Visualizes the molecule based on contact type.

### `init_local_tab(self)`

**Module:** `tabs/local_tab.py`

Initializes the local tab interface.

### `init_multi_file_tab(self)`

**Module:** `tabs/multiple_file_tab.py`

Initializes the multi-file tab interface.

### `init_single_file_tab(self)`

**Module:** `tabs/single_file_tab.py`

Initializes the single-file tab interface.

## Initialization Functions

### `check_installed_packages(requirements_list)`

**Module:** `initialization_checks.py`

Checks to see if the necessary packages are installed.

### `conda_init(user_install)`

**Module:** `initialization_checks.py`

Initializes conda in powershell.

### `get_requirements(req_path)`

**Module:** `initialization_checks.py`

Gets the required packages from the yml file.

### `install_failed(reqs=requirements_file)`

**Module:** `initialization_checks.py`

Give instructions on how to install dependencies if installation fails.

### `is_conda_installed()`

**Module:** `initialization_checks.py`

Checks to see if conda is installed on the system.

### `is_path_user(path)`

**Module:** `initialization_checks.py`

Checks if a path is system or user.

### `linux_install(env=LINUX_ENV_FIXED, reqs=LINUX_REQS_FIXED)`

**Module:** `initialization_checks.py`

Linux install.

### `mac_install(env=pymol_env, reqs=requirements_file)`

**Module:** `initialization_checks.py`

Mac install.

### `pymol_install(env=pymol_env, reqs=requirements_file)`

**Module:** `initialization_checks.py`

Tries install with pymol terminal.

### `register_pymol_functions()`

**Module:** `initialization_checks.py`

Register functions as PyMOL commands.

### `win_install(env=pymol_env, reqs=requirements_file)`

**Module:** `initialization_checks.py`

Windows install.

## Function Statistics

- **Calculating Functions**: 6
- **Plotting Functions**: 6
- **Importing Functions**: 1
- **Exporting Functions**: 3
- **Analysis Functions**: 6
- **Utility Functions**: 36
- **GUI Functions**: 43
- **Initialization Functions**: 11
- **Total**: 112

## Notes

- `initialization_checks.register_pymol_functions` currently imports several legacy modules that are not present in this tree (for example `string_pdb`, `secondary_struc_cmap`, `retrieve_cif`, and `export_circuit`).
- This documentation intentionally lists only callables defined in files currently present in the project.

*Last Updated: April 09, 2026*