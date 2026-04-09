# Protein Circuit Topology Plugin - Complete API Documentation

This document provides a comprehensive reference of **ALL 126 callable entry points** available in the Protein Circuit Topology Plugin, including their parameters, return values, and descriptions.

**Total Functions:** 126 across 54 Python files

## Table of Contents

1. [Calculating Functions](#calculating-functions) (13 functions)
2. [Plotting Functions](#plotting-functions) (7 functions)
3. [Importing Functions](#importing-functions) (5 functions)
4. [Exporting Functions](#exporting-functions) (5 functions)
5. [Analysis Functions](#analysis-functions) (6 functions)
6. [Utility Functions](#utility-functions) (36 functions)
7. [GUI Functions](#gui-functions) (42 functions)
8. [Initialization Functions](#initialization-functions) (12 functions)

---

## Calculating Functions

### `get_cmap(chain, level='chain', cutoff_distance=4.5, cutoff_numcontacts=5, exclude_neighbour=3)`

Creates a residue-residue contact map (as a list of contacts) for a single chain or a whole model.

**Module:** `functions/calculating/get_cmap.py`

**Parameters:**
- `chain` (Bio.PDB.Chain.Chain or Bio.PDB.Model.Model): The chain or model object to analyze.
- `level` (str, optional): 'chain' for single chain analysis, 'model' for whole model analysis. Defaults to 'chain'.
- `cutoff_distance` (float, optional): Maximum distance (in Angstroms) between atoms to consider a contact. Defaults to 4.5.
- `cutoff_numcontacts` (int, optional): Minimum number of atomic contacts required to define a residue-residue contact. Defaults to 5.
- `exclude_neighbour` (int, optional): Minimum sequence separation (in residues) to consider a contact. Defaults to 3.

**Returns:**
- `tuple`: Tuple containing:
  - Array of contact indices.
  - Array of residue numbering.
  - Protein ID string.
  - List of residue names.

---

### `get_cmap_com(chain, cutoff_distance=7, exclude_neighbour=3)`

Creates a residue-residue contact map based on the Centre of Mass (COM) of the residues.

**Module:** `functions/calculating/get_cmap_com.py`

**Parameters:**
- `chain` (Bio.PDB.Chain.Chain): The protein chain object.
- `cutoff_distance` (float, optional): Maximum distance (in Angstroms) between COMs to consider a contact. Defaults to 7.
- `exclude_neighbour` (int, optional): Minimum sequence separation (in residues) to consider a contact. Defaults to 3.

**Returns:**
- `tuple`: (index, numbering, com)

---

### `get_cmap_cog(chain, cutoff_distance=4.5, exclude_neighbour=3)`

Creates a residue-residue contact map based on the Centre of Geometry (COG) of the residues.

**Module:** `functions/calculating/get_cmap_cog.py`

**Parameters:**
- `chain` (Bio.PDB.Chain.Chain): The protein chain object.
- `cutoff_distance` (float, optional): Maximum distance (in Angstroms) between COGs to consider a contact. Defaults to 4.5.
- `exclude_neighbour` (int, optional): Minimum sequence separation (in residues) to consider a contact. Defaults to 3.

**Returns:**
- `tuple`: (index, numbering)

---

### `get_matrix(index, protid)`

Creates a topological relationship matrix for a residue contact map.

**Module:** `functions/calculating/get_matrix.py`

**Parameters:**
- `index` (numpy.ndarray): Array containing contact indices.
- `protid` (str): Protein identifier.

**Returns:**
- `tuple`: (mat, stats) or (mat, stats, chainstats) depending on single/multi-chain analysis

---

### `get_stats(mat)`

Calculates the percentage of entangled contacts (Parallel and Cross) further along the diagonal.

**Module:** `functions/calculating/get_stats.py`

**Parameters:**
- `mat` (numpy.ndarray): The topological relationship matrix.

**Returns:**
- `numpy.ndarray`: An array containing the percentage of entangled contacts for each diagonal.

---

### `energy_cmap(index, numbering, res_names, protid, potential_sign='-')`

Applies an energy filter to an existing residue contact map based on a potential matrix.

**Module:** `functions/calculating/energy_cmap.py`

**Parameters:**
- `index` (numpy.ndarray): Array of contact indices.
- `numbering` (list or numpy.ndarray): List of residue numbers/identifiers.
- `res_names` (list): List of residue names corresponding to the numbering.
- `protid` (str): Protein identifier.
- `potential_sign` (str, optional): The sign of the potential to filter by ('+' or '-'). Defaults to '-'.

**Returns:**
- `tuple`: (energy_cmap, protid)

---

### `string_pdb(index, numbering, threshold)`

Analyzes the contact map to identify and characterize circuits based on Anatoly's circuit theory.

**Module:** `functions/calculating/string_pdb.py`

**Parameters:**
- `index` (numpy.ndarray): Array of contact indices.
- `numbering` (list or numpy.ndarray): List of residue numbers/identifiers.
- `threshold` (int): Threshold for defining long-range contacts.

**Returns:**
- `tuple`: (segnums, meanlength, segends)

---

### `secondary_struc_cmap(chain, sequence, structure, cutoff_distance=4.5, cutoff_numcontacts=10, exclude_neighbour=3, ss_elements=['H', 'E', 'B', 'b', 'G'])`

Creates a segment-segment contact map based on secondary structure elements.

**Module:** `functions/calculating/secondary_struc_cmap.py`

**Parameters:**
- `chain` (Bio.PDB.Chain.Chain): The protein chain object.
- `sequence` (str): The amino acid sequence.
- `structure` (str): The secondary structure string.
- `cutoff_distance` (float, optional): Maximum distance (in Angstroms) between atoms to consider a contact. Defaults to 4.5.
- `cutoff_numcontacts` (int, optional): Minimum number of atomic contacts required to define a segment-segment contact. Defaults to 10.
- `exclude_neighbour` (int, optional): Minimum sequence separation (in residues) to consider a contact. Defaults to 3.
- `ss_elements` (list, optional): List of secondary structure codes to consider as segments. Defaults to `['H', 'E', 'B', 'b', 'G']`.

**Returns:**
- `tuple`: (index, segment)

---

### `secondary_struc_filter(index, struc, filtered_structures=['H', 'E'], ss_elements=['H', 'E', 'B', 'b', 'G', 'b'])`

Filters out residue contacts that occur within the same secondary structure element.

**Module:** `functions/calculating/secondary_struc_filter.py`

**Parameters:**
- `index` (numpy.ndarray): Array of contact indices.
- `struc` (str): The secondary structure string.
- `filtered_structures` (list, optional): List of secondary structure types to filter out contacts within. Defaults to `['H', 'E']`.
- `ss_elements` (list, optional): List of secondary structure codes considered as distinct elements. Defaults to `['H', 'E', 'B', 'b', 'G', 'b']`.

**Returns:**
- `tuple`: (index_filtered, struc_id)

---

### `glob_score(mat)`

Calculates an advanced globularity score for a protein based on its topological relationship matrix.

**Module:** `functions/calculating/glob_score.py`

**Parameters:**
- `mat` (numpy.ndarray): The topological relationship matrix.

**Returns:**
- `float`: The calculated globularity score.

---

### `length_filter(index, distance, mode='<')`

Filters contact indices based on sequence separation distance.

**Module:** `functions/calculating/length_filter.py`

**Parameters:**
- `index` (numpy.ndarray): Array of contact indices.
- `distance` (int): The distance threshold for filtering.
- `mode` (str, optional): The filtering mode ('<' for less than or equal to, '>' for greater than or equal to). Defaults to '<'.

**Returns:**
- `numpy.ndarray`: The filtered array of contact indices.

---

### `contact_order(chain, cutoff_distance)`

Calculates the absolute and relative contact order for a protein chain.

**Module:** `functions/calculating/contact_order.py`

**Parameters:**
- `chain` (Bio.PDB.Chain.Chain): The protein chain object.
- `cutoff_distance` (float): The cutoff distance (in Angstroms) for defining contacts.

**Returns:**
- `tuple`: (chain_length, absolute_contact_order, relative_contact_order)

---

### `local_ct(index, mat, numbering)`

Calculates local circuit topology statistics for each residue.

**Module:** `functions/calculating/local_ct.py`

**Parameters:**
- `index` (numpy.ndarray): Array of contact indices.
- `mat` (numpy.ndarray): The topological relationship matrix.
- `numbering` (list or numpy.ndarray): List of residue numbers/identifiers.

**Returns:**
- `dict`: Dictionary mapping residue indices to topology counts {'P', 'IP', 'X', 'S'}

---

## Plotting Functions

### `circuit_plot(index, protid, numbering)`

Plots the circuit topology of a protein as a series of arcs.

**Module:** `functions/plots/circuit_plot.py`

**Parameters:**
- `index` (numpy.ndarray): Array of contact indices.
- `protid` (str): Protein identifier.
- `numbering` (list or numpy.ndarray): List of residue numbers/identifiers.

**Returns:**
- `None`: Displays a matplotlib plot.

---

### `matrix_plot(mat, protid)`

Plots the topological relationship matrix for a single chain.

**Module:** `functions/plots/matrix_plot.py`

**Parameters:**
- `mat` (numpy.ndarray): The topological relationship matrix.
- `protid` (str): Protein identifier.

**Returns:**
- `None`: Displays a matplotlib plot.

---

### `matrix_plot_model(mat, protid)`

Plots the topological relationship matrix for a whole model (multiple chains).

**Module:** `functions/plots/matrix_plot_model.py`

**Parameters:**
- `mat` (numpy.ndarray): The topological relationship matrix.
- `protid` (str): Protein identifier.

**Returns:**
- `None`: Displays a matplotlib plot.

---

### `stats_plot(entangled, psc, protid)`

Plots the fraction of entangled contacts versus distance from the diagonal and a pie chart of contact types.

**Module:** `functions/plots/stats_plot.py`

**Parameters:**
- `entangled` (numpy.ndarray): Array of entangled contact fractions.
- `psc` (list): List of contact type counts (P, S, C, etc.).
- `protid` (str): Protein identifier.

**Returns:**
- `None`: Displays a matplotlib figure.

---

### `autopct_funct(pct)`

Helper function for formatting percentages in pie charts.

**Module:** `functions/plots/stats_plot.py`

**Parameters:**
- `pct` (float): The percentage value.

**Returns:**
- `str`: Formatted percentage string.

---

### `local_topology_plot(index, mat, numbering, protid, siteid, relation)`

Creates multiple plots highlighting local topology around a specific residue site.

**Module:** `functions/plots/local_topology_plot.py`

**Parameters:**
- `index` (numpy.ndarray): Array of contact indices.
- `mat` (numpy.ndarray): The topological relationship matrix.
- `numbering` (list or numpy.ndarray): List of residue numbers/identifiers.
- `protid` (str): Protein identifier.
- `siteid` (int): The residue index to highlight.
- `relation` (str): The relationship type to highlight ('X', 'S', 'P', or 'IP').

**Returns:**
- `None`: Displays three matplotlib plots.

---

### `pymol(protid, index, numbering, chain1)`

Generates PyMOL script for visualizing contacts.

**Module:** `functions/plots/pymol.py`

**Parameters:**
- `protid` (str): Protein identifier.
- `index` (numpy.ndarray): Array of contact indices.
- `numbering` (list or numpy.ndarray): List of residue numbers/identifiers.
- `chain1` (str): Chain identifier.

**Returns:**
- `None`: Writes a .pml PyMOL script file.

---

## Importing Functions

### `retrieve_chain(input_file, chainid=0)`

Retrieves a specific chain from a PDB or MMCIF file.

**Module:** `functions/importing/retrieve_chain.py`

**Parameters:**
- `input_file` (str): Path to the input PDB or MMCIF file.
- `chainid` (int or str, optional): The chain ID to retrieve. Defaults to 0.

**Returns:**
- `tuple`: (chain, protid)

---

### `retrieve_cif(prot_id)`

Downloads a single MMCIF file from the PDB.

**Module:** `functions/importing/retrieve_cif.py`

**Parameters:**
- `prot_id` (str): The PDB ID of the protein to download.

**Returns:**
- `None`: Downloads the file to 'input_files/cif/' directory.

---

### `retrieve_cif_list()`

Downloads multiple MMCIF files specified in 'input_files/protlist.txt'.

**Module:** `functions/importing/retrieve_cif_list.py`

**Parameters:**
- None

**Returns:**
- `None`: Downloads files to 'input_files/cif/' directory.

---

### `retrieve_secondary_struc(chain, input_path)`

Retrieves secondary structure information using DSSP.

**Module:** `functions/importing/retrieve_secondary_struc.py`

**Parameters:**
- `chain` (Bio.PDB.Chain.Chain): The protein chain object.
- `input_path` (str): Path to the PDB file.

**Returns:**
- `tuple`: (seq, struc)

---

### `stride_secondary_struc(stride_file)`

Reads a STRIDE output file and extracts the secondary structure and sequence.

**Module:** `functions/importing/stride_secondary_struc.py`

**Parameters:**
- `stride_file` (str): The name of the STRIDE file (located in 'input_files/stride/').

**Returns:**
- `tuple`: (struc, seq)

---

## Exporting Functions

### `export_psc(psclist, output_dir)`

Exports the counts of Parallel, Series, and Cross contacts to a CSV file.

**Module:** `functions/exporting/export_psc.py`

**Parameters:**
- `psclist` (list): A list of PSC statistics.
- `output_dir` (str): The directory to save the CSV file.

**Returns:**
- `None`: Saves 'pscresults.csv'.

---

### `export_cmap3(index, protid, numbering, output_dir)`

Exports a residue contact map (as a binary matrix) to a CSV file.

**Module:** `functions/exporting/export_cmap3.py`

**Parameters:**
- `index` (numpy.ndarray): Array of contact indices.
- `protid` (str): Protein identifier.
- `numbering` (list or numpy.ndarray): List of residue numbers/identifiers.
- `output_dir` (str): The directory to save the CSV file.

**Returns:**
- `None`: Saves '{protid}_cmap3.csv'.

---

### `export_mat(index, mat, protid, output_dir)`

Exports the topological relationship matrix to a CSV file.

**Module:** `functions/exporting/export_mat.py`

**Parameters:**
- `index` (numpy.ndarray): Array of contact indices.
- `mat` (numpy.ndarray): The topological relationship matrix.
- `protid` (str): Protein identifier.
- `output_dir` (str): The directory to save the CSV file.

**Returns:**
- `None`: Saves '{protid}_mat.csv'.

---

### `export_cmap4(cmap4, segment, structure, protid)`

Exports a segment contact map (as a binary matrix) to a CSV file.

**Module:** `functions/exporting/export_cmap4.py`

**Parameters:**
- `cmap4` (numpy.ndarray): Array of segment contact indices.
- `segment` (numpy.ndarray): Array mapping residues to segment IDs.
- `structure` (str): The secondary structure string.
- `protid` (str): Protein identifier.

**Returns:**
- `None`: Saves '{protid}_cmap4.csv'.

---

### `export_circuit(circlist)`

Exports circuit information to a CSV file.

**Module:** `functions/exporting/export_circuit.py`

**Parameters:**
- `circlist` (list): A list of circuit data (protid, segnums, meanlength, segends).

**Returns:**
- `None`: Saves 'circuitlist.csv'.

---

## Analysis Functions

### `run_standard_analysis(self)`

Runs the standard single-file circuit topology analysis.

**Module:** `analysis/single_file_analysis.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`: Performs analysis, generates plots, and exports data.

---

### `run_multi_analysis(self)`

Runs the multi-file circuit topology analysis.

**Module:** `analysis/multiple_file_analysis.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`: Iterates through files, performs analysis, generates plots, and exports data.

---

### `run_local_ct(self)`

Runs the local circuit topology analysis.

**Module:** `analysis/local_ct_analysis.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`: Performs local analysis and generates plots/exports.

---

### `run_single_frame_analysis(self)`

Runs circuit topology analysis for a single frame of a trajectory.

**Module:** `analysis/single_frame_analysis.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`: Analyzes a single frame and generates plots/exports.

---

### `toggle_frame_controls(self, enabled)`

Toggles the enabled state of the frame selector and run button.

**Module:** `analysis/single_frame_analysis.py`

**Parameters:**
- `self` (Any): The main GUI class instance.
- `enabled` (bool): True to enable, False to disable.

**Returns:**
- `None`

---

### `visualize_molecule(self, contact_type)`

Visualizes the circuit topology on the selected molecule in PyMOL by coloring residues.

**Module:** `analysis/visualization.py`

**Parameters:**
- `self` (Any): The main GUI class instance.
- `contact_type` (str): The type of contact to visualize ('P', 'S', 'X').

**Returns:**
- `None`: Colors the molecule in PyMOL.

---

## Utility Functions

### Topology Utilities

#### `get_topology_vector(mat, index, topology_type, numbering)`

Calculates a topology vector representing the density of a specific contact type for each residue.

**Module:** `utils/topology.py`

**Parameters:**
- `mat` (numpy.ndarray): The topological relationship matrix.
- `index` (numpy.ndarray): Array of contact indices.
- `topology_type` (str): The type of topology to calculate ('P', 'S', 'X').
- `numbering` (list or numpy.ndarray): List of residue numbers/identifiers.

**Returns:**
- `numpy.ndarray`: The calculated topology vector.

---

#### `color_by_topology(molecule_name, topology_vector, numbering, topology_type)`

Colors a PyMOL object based on a topology vector.

**Module:** `utils/topology.py`

**Parameters:**
- `molecule_name` (str): The name of the PyMOL object to color.
- `topology_vector` (numpy.ndarray): The topology vector containing values for coloring.
- `numbering` (list or numpy.ndarray): List of residue numbers.
- `topology_type` (str): The type of topology ('P', 'S', 'X').

**Returns:**
- `None`: Colors the object in PyMOL.

---

### Folding Score Utilities

#### `get_folding_score(mat, index, numbering)`

Calculate the folding score based on the topology data.

**Module:** `utils/folding_score.py`

**Parameters:**
- `mat` (numpy.ndarray): The topological relationship matrix.
- `index` (numpy.ndarray): Array of contact indices.
- `numbering` (list or numpy.ndarray): List of residue numbers/identifiers.

**Returns:**
- `float`: The calculated folding score.

---

### Value Retrieval Utilities

#### `get_values(self)`

Retrieves parameters for single-file analysis from the GUI.

**Module:** `utils/get_values.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `dict`: Dictionary containing analysis parameters.

---

#### `get_local_values(self)`

Retrieves parameters for local analysis from the GUI.

**Module:** `utils/get_values.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `dict`: Dictionary containing local analysis parameters.

---

#### `get_multiple_values(self)`

Retrieves parameters for multi-file analysis from the GUI.

**Module:** `utils/get_values.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `dict`: Dictionary containing multi-file analysis parameters.

---

#### `get_vis_vals(self)`

Retrieves visualization parameters from the GUI.

**Module:** `utils/get_values.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `dict`: Dictionary containing visualization parameters.

---

### Directory and File Utilities

#### `choose_file(self)`

Opens a file dialog to select a structure file for single-file analysis.

**Module:** `utils/directory.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`: Updates self.selected_file.

---

#### `choose_local_file(self)`

Opens a file dialog to select a structure file for local analysis.

**Module:** `utils/directory.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`: Updates self.local_selected_file.

---

#### `choose_output_dir(self)`

Opens a directory dialog to select the output directory for single-file analysis results.

**Module:** `utils/directory.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`: Updates self.selected_output_dir.

---

#### `choose_local_output_dir(self)`

Opens a directory dialog to select the output directory for local analysis results.

**Module:** `utils/directory.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`: Updates self.selected_output_dir_local.

---

#### `choose_output_dir_multi(self)`

Opens a directory dialog to select the output directory for multi-file analysis results.

**Module:** `utils/directory.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`: Updates self.selected_output_dir_multi.

---

#### `choose_input_dir_multi(self)`

Opens a directory dialog to select the input directory containing PDB files for multi-file analysis.

**Module:** `utils/directory.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`: Updates self.selected_input_dir_multi and frame selector range.

---

#### `set_label_text_elided(file_path, label)`

Sets the text of a QLabel to an elided version of the file path if it's too long.

**Module:** `utils/directory.py`

**Parameters:**
- `file_path` (str): The full file path.
- `label` (QLabel): The label widget to update.

**Returns:**
- `None`: Updates the label with elided text.

---

### Clear File Utilities

#### `clear_selected_single_file(self)`

Clears the currently selected single file and updates the UI.

**Module:** `utils/clear_file.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`

---

#### `clear_selected_local_file(self)`

Clears the currently selected local file and updates the UI.

**Module:** `utils/clear_file.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`

---

### Non-Polymer Utilities

#### `show_warning_dialog(self)`

Shows a warning dialog before removing non-polymer atoms.

**Module:** `utils/non_polymer.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`

---

#### `remove_non_polymer_atoms()`

Removes all non-polymer atoms from the PyMOL session.

**Module:** `utils/non_polymer.py`

**Parameters:**
- None

**Returns:**
- `None`

---

#### `has_non_polymer_atoms()`

Checks if there are any non-polymer atoms in the PyMOL session.

**Module:** `utils/non_polymer.py`

**Parameters:**
- None

**Returns:**
- `bool`: True if non-polymer atoms exist.

---

#### `new_file_has_non_polymer_atoms(obj_name)`

Checks if a specific object contains non-polymer atoms.

**Module:** `utils/non_polymer.py`

**Parameters:**
- `obj_name` (str): The name of the object to check.

**Returns:**
- `bool`: True if the object contains non-polymer atoms.

---

### Object Change Handlers

#### `handle_standard_object_change(self, obj_name)`

Handles changes to the selected object in the standard analysis tab.

**Module:** `utils/object_change.py`

**Parameters:**
- `self` (Any): The main GUI class instance.
- `obj_name` (str): The name of the newly selected object.

**Returns:**
- `None`

---

#### `handle_local_object_change(self, obj_name)`

Handles changes to the selected object in the local analysis tab.

**Module:** `utils/object_change.py`

**Parameters:**
- `self` (Any): The main GUI class instance.
- `obj_name` (str): The name of the newly selected object.

**Returns:**
- `None`

---

### Residue Utilities

#### `get_residue_range(self, obj_name)`

Retrieves the residue range for each chain in the specified object.

**Module:** `utils/residues.py`

**Parameters:**
- `self` (Any): The main GUI class instance.
- `obj_name` (str): The name of the object to analyze.

**Returns:**
- `None`: Updates self.curr_chain_residues.

---

#### `update_residue_range(self)`

Updates the residue range spinbox based on the currently selected chain.

**Module:** `utils/residues.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`

---

### Helper Utilities

#### `update_chain_combo_box(self)`

Updates the chain combo box with the chains available in the currently selected object.

**Module:** `utils/helpers.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`

---

#### `make_info_button(tooltip)`

Creates a small info button with a tooltip.

**Module:** `utils/helpers.py`

**Parameters:**
- `tooltip` (str): The text to display in the tooltip.

**Returns:**
- `QPushButton`: The configured info button.

---

#### `init_timers(self)`

Initializes timers for updating object lists.

**Module:** `utils/helpers.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`

---

#### `object_exists(name)`

Checks if a PyMOL object exists.

**Module:** `utils/helpers.py`

**Parameters:**
- `name` (str): The name of the object.

**Returns:**
- `bool`: True if the object exists.

---

### Update Utilities

#### `update_list(self)`

Updates the list of available objects in the single-file analysis dropdown.

**Module:** `utils/updates.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`

---

#### `update_local_list(self)`

Updates the list of available objects in the local analysis dropdown.

**Module:** `utils/updates.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`

---

#### `update_output_widgets(self)`

Updates the visibility of output widgets in the single-file analysis tab.

**Module:** `utils/updates.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`

---

#### `update_output_widgets_local(self)`

Updates the visibility of output widgets in the local analysis tab.

**Module:** `utils/updates.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`

---

#### `update_output_widgets_multi(self)`

Updates the visibility of output widgets in the multi-file analysis tab.

**Module:** `utils/updates.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`

---

### Trajectory Utilities

#### `select_mol_file(self)`

Opens a file dialog to select a structure file for trajectory analysis.

**Module:** `utils/trajectory.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`: Loads file into PyMOL.

---

#### `select_xtc_file(self)`

Opens a file dialog to select a trajectory file.

**Module:** `utils/trajectory.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`: Loads trajectory into PyMOL.

---

#### `export_frames_from_traj(self)`

Exports each frame of the loaded trajectory as a separate PDB file.

**Module:** `utils/trajectory.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`: Exports frames to selected directory.

---

## GUI Functions

### Plugin GUI Entry Point

#### `run_plugin_gui()`

Runs or focuses the plugin dialog window.

**Module:** `__init__.py`

**Parameters:**
- None

**Returns:**
- `object`: Active `CTDialog` instance.

---

### Tab Initialization Functions

#### `init_single_file_tab(self)`

Initializes the single-file analysis tab of the GUI.

**Module:** `tabs/single_file_tab.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`

---

#### `init_multi_file_tab(self)`

Initializes the multi-file analysis tab of the GUI.

**Module:** `tabs/multiple_file_tab.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`

---

#### `init_local_tab(self)`

Initializes the local circuit topology analysis tab of the GUI.

**Module:** `tabs/local_tab.py`

**Parameters:**
- `self` (Any): The main GUI class instance.

**Returns:**
- `None`

---

### `CTDialog` Class Methods (38 methods)

The `gui_class.py` file contains the main `CTDialog` class. Most methods are Qt slots that delegate to functions in `utils/`, `analysis/`, and `tabs/` modules.

**Module:** `gui_class.py`

**Methods:**
- `get_values(self)`
- `get_local_values(self)`
- `get_multiple_values(self)`
- `get_vis_vals(self)`
- `clear_selected_local_file(self)`
- `clear_selected_single_file(self)`
- `choose_file(self)`
- `choose_local_file(self)`
- `choose_output_dir(self)`
- `choose_local_output_dir(self)`
- `choose_input_dir_multi(self)`
- `choose_output_dir_multi(self)`
- `handle_local_object_change(self, obj_name=None)`
- `handle_standard_object_change(self, obj_name=None)`
- `show_warning_dialog(self)`
- `get_residue_range(self, obj_name=None)`
- `update_residue_range(self)`
- `update_chain_combo_box(self)`
- `init_timers(self)`
- `update_list(self)`
- `update_local_list(self)`
- `update_output_widgets(self)`
- `update_output_widgets_local(self)`
- `update_output_widgets_multi(self)`
- `select_mol_file(self)`
- `select_xtc_file(self)`
- `export_frames_from_traj(self)`
- `init_local_tab(self)`
- `init_single_file_tab(self)`
- `init_multi_file_tab(self)`
- `run_local_ct(self)`
- `run_standard_analysis(self)`
- `run_single_frame_analysis(self)`
- `run_multi_analysis(self)`
- `visualize_molecule(self, contact_type)`
- `toggle_frame_controls(self, enabled)`
- `__init__(self, parent=None)`
- `init_ui(self)`

**Returns:**
- Wrapper and UI methods return `None` unless delegated function behavior differs.

---

## Initialization Functions

### `__init_plugin__(app=None)`

Initializes the plugin, performs dependency checks/installation flow, registers PyMOL commands, and adds the plugin menu item.

**Module:** `__init__.py`

**Parameters:**
- `app` (object, optional): Optional application object passed by PyMOL.

**Returns:**
- `None`

---

### `is_path_user(path)`

Checks if a given path is within the user's home directory.

**Module:** `initialization_checks.py`

**Parameters:**
- `path` (str): The path to check.

**Returns:**
- `bool`: True if the path is within the user's home directory.

---

### `pymol_install(env=pymol_env, reqs=requirements_file)`

Attempts to install dependencies using the PyMOL terminal and conda.

**Module:** `initialization_checks.py`

**Parameters:**
- `env` (str, optional): Path to the PyMOL environment.
- `reqs` (str, optional): Path to the requirements file.

**Returns:**
- `bool`: True if installation was successful.

---

### `install_failed(reqs=requirements_file)`

Prints instructions for manual installation of dependencies.

**Module:** `initialization_checks.py`

**Parameters:**
- `reqs` (str, optional): Path to the requirements file.

**Returns:**
- `None`

---

### `get_requirements(req_path)`

Parses the requirements.yml file to get a list of required packages.

**Module:** `initialization_checks.py`

**Parameters:**
- `req_path` (str): Path to the requirements file.

**Returns:**
- `list`: A list of package names.

---

### `check_installed_packages(requirements_list)`

Checks if the required packages are installed in the current environment.

**Module:** `initialization_checks.py`

**Parameters:**
- `requirements_list` (list): List of package names to check.

**Returns:**
- `tuple`: (all_installed: bool, packages_list: list)

---

### `is_conda_installed()`

Checks if conda is installed on the system.

**Module:** `initialization_checks.py`

**Parameters:**
- None

**Returns:**
- `tuple`: (is_installed: bool, path: str)

---

### `conda_init(user_install)`

Initializes conda for PowerShell.

**Module:** `initialization_checks.py`

**Parameters:**
- `user_install` (bool): True if PyMOL is installed in a user directory.

**Returns:**
- `bool`: True if initialization was successful.

---

### `win_install(env=pymol_env, reqs=requirements_file)`

Performs installation on Windows using PowerShell and conda.

**Module:** `initialization_checks.py`

**Parameters:**
- `env` (str, optional): Path to the PyMOL environment.
- `reqs` (str, optional): Path to the requirements file.

**Returns:**
- `bool`: True if installation was successful.

---

### `mac_install(env=pymol_env, reqs=requirements_file)`

Performs installation on macOS using pip.

**Module:** `initialization_checks.py`

**Parameters:**
- `env` (str, optional): Path to the PyMOL environment.
- `reqs` (str, optional): Path to the requirements file.

**Returns:**
- `bool`: True if installation was successful.

---

### `linux_install(env=LINUX_ENV_FIXED, reqs=LINUX_REQS_FIXED)`

Performs installation on Linux using pip (and conda for DSSP if needed).

**Module:** `initialization_checks.py`

**Parameters:**
- `env` (str, optional): Path to the PyMOL environment.
- `reqs` (str, optional): Path to the requirements file.

**Returns:**
- `bool`: True if installation was successful.

---

### `register_pymol_functions()`

Register all functions as PyMOL commands.

**Module:** `initialization_checks.py`

**Parameters:**
- None

**Returns:**
- `None`: Extends plugin functions to the PyMOL command line.

---

## Function Statistics

### By Category
- **Calculating Functions**: 13
- **Plotting Functions**: 7
- **Importing Functions**: 5
- **Exporting Functions**: 5
- **Analysis Functions**: 6
- **Utility Functions**: 36
- **GUI Functions**: 42
- **Initialization Functions**: 12

### By Module Type
- **Core Functions** (calculating, plotting, importing, exporting): 30
- **Analysis Orchestration**: 6
- **GUI & User Interaction**: 42
- **Utility & Helper Functions**: 36
- **Setup & Installation**: 12

### **Total Functions: 126**

---

## Usage Patterns

### Typical Analysis Workflow

```python
# 1. Load structure
chain, protid = retrieve_chain('protein.pdb')

# 2. Generate contact map
index, numbering, protid, res_names = get_cmap(chain)

# 3. Create topology matrix
mat, stats = get_matrix(index, protid)

# 4. Analyze and visualize
entangled = get_stats(mat)
circuit_plot(index, protid, numbering)
matrix_plot(mat, protid)

# 5. Export results
export_cmap3(index, protid, numbering, 'output/')
export_mat(index, mat, protid, 'output/')
```

### GUI-Driven Analysis

The GUI functions handle the entire workflow automatically:
- `run_standard_analysis()` for single files
- `run_multi_analysis()` for batch processing
- `run_local_ct()` for local topology analysis
- `run_single_frame_analysis()` for trajectory frames

---

## Configuration

### Config Constants

**Module:** `utils/config.py`

- `SECTION_STYLESHEET`: QGroupBox styling
- `INFO_BUTTON_STYLE`: Info button styling

---

## Notes

1. **GUI Functions**: Most utility functions are designed to be used as methods of the GUI class instance (passed as `self`).

2. **PyMOL Integration**: After calling `register_pymol_functions()`, all core functions become available as PyMOL commands.

3. **File Handling**: Most functions handle both PDB and CIF formats automatically.

4. **Error Handling**: Functions generally print errors to console and return safe defaults.

5. **Cross-Platform**: Installation and file handling functions are OS-aware (Windows, Mac, Linux).

---

*Last Updated: April 9, 2026*

*Total Functions Documented: 126*
