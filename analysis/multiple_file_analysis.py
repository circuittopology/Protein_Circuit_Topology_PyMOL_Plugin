import os
import sys
from pathlib import Path
import matplotlib.pyplot as plt
from typing import Any

from pymol import cmd
from pymol.Qt import QtWidgets
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
# pylint: disable=wrong-import-position
from functions.calculating.get_matrix import get_matrix
from functions.calculating.get_cmap import get_cmap
from functions.calculating.energy_cmap import energy_cmap
from functions.calculating.length_filter import length_filter
from functions.calculating.get_stats import get_stats

from functions.importing.retrieve_chain import retrieve_chain

from functions.plots.matrix_plot import matrix_plot
from functions.plots.circuit_plot import circuit_plot
from functions.plots.matrix_plot_model import matrix_plot_model
from functions.plots.stats_plot import stats_plot

from functions.exporting.export_mat import export_mat
from functions.exporting.export_cmap3 import export_cmap3
from functions.exporting.export_psc import export_psc

from utils.non_polymer import has_non_polymer_atoms
from utils.config import WARN_MSG, CHECKBOX_WARN

# Slight rewrite to match their notebook code because we had bugs
def run_multi_analysis(self: Any) -> None:
    """
    Runs the multi-file circuit topology analysis.
    Iterates through files in the selected directory, performs analysis, and generates plots/exports.

    Args:
        self: The main GUI class instance.
    """
    # check for non-polymer atoms
    if has_non_polymer_atoms():
        QtWidgets.QMessageBox.warning(self, "Warning", WARN_MSG)

    vals = self.get_multiple_values()
    # Yes/No options (retrieving once rather than every time in for loop)
    multi_energy_filtering = vals["energy_filtering"]
    multi_len_filtering = vals["length_filtering"]
    multi_circuit_plot = vals["circuit_plot"]
    multi_matrix_plot = vals["matrix_plot"]
    multi_stats_plot = vals["stats_plot"]
    multi_export_cmap3 = vals["export_cmap3"]
    multi_psc = vals["export_psc"]
    multi_export_mat = vals["export_mat"]
    multi_input_dir = vals["directory"]
    multi_traj_dir = vals["traj_directory"]
    multi_plot_psc = vals["plot_psc"]
    if not multi_input_dir and not multi_traj_dir:
        QtWidgets.QMessageBox.warning(self, "Error", "No input directory selected!")
        return

    if multi_traj_dir:
        path = multi_traj_dir
    else:
        path = multi_input_dir

    if not os.path.exists(path):
        QtWidgets.QMessageBox.warning(self, "Error", f"The input directory does not exist: {path}")
        return

    output_dir = vals["output_directory"]

    if not output_dir:
        if multi_export_cmap3 or multi_export_mat or multi_psc:
            QtWidgets.QMessageBox.warning(
                self,
                "Error",
                f"An output directory has not been selected: {output_dir}"
            )
            return

    number_of_files = len(os.listdir(path))
    psclist = []
    p = []
    s = []
    x = []

    # Numeric options (retrieving once rather than every time in for loop)
    cutoff_dist_multi = vals["cutoff_distance"]
    multi_neighbours = vals["exclude_neighbour"]
    multi_num_contacts = vals["cutoff_numcontacts"]
    multi_energy_mode = vals["energy_filtering_mode"]
    multi_filtering_dist = vals["filtering_distance"]
    multi_filter_mode = vals["length_filter_mode"]

    if not (multi_circuit_plot or multi_matrix_plot or multi_stats_plot or multi_export_cmap3 or multi_export_mat or multi_psc):
        QtWidgets.QMessageBox.warning(self, "Error", CHECKBOX_WARN)
        return

    if multi_circuit_plot or multi_matrix_plot or multi_stats_plot or multi_export_cmap3 or multi_export_mat:
        confirm = QtWidgets.QMessageBox.question(self,
                                                    "Continue multi-file analysis",
                                                    f"Are you sure you want to continue with multi-file analysis?\n\nIt will create a plot / export a .csv for each of your {number_of_files} files!",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if confirm != QtWidgets.QMessageBox.Yes:
            print("Multi-file analysis was aborted.")
            return

    for num, files in enumerate(os.listdir(path)):
        if files.endswith((".pdb", ".cif")):
            try:
                multi_full_path = os.path.join(path, files)
                multi_obj = os.path.splitext(os.path.basename(multi_full_path))[0]
                cmd.load(multi_full_path, multi_obj)
                cmd.remove("not polymer")
                multi_obj_chains = cmd.get_chains(multi_obj)
                multi_chain, protid = retrieve_chain(multi_full_path)
                print(f'{files} - {num + 1}/{number_of_files}')
            except Exception as e:
                print(f'{files} - {e}')
                continue
        else:
            continue

        if len(multi_obj_chains) > 1:
            multi_level = "model"
            print(
                "The object %s has multiple chains. Performing multi-chain CT analysis...",
                multi_obj
            )
        else:
            multi_level = "chain"

        idx, numbering, protid, res_names = get_cmap(multi_chain, level=multi_level,
                                                        cutoff_distance=cutoff_dist_multi,
                                                        cutoff_numcontacts=multi_num_contacts,
                                                        exclude_neighbour=multi_neighbours)

        if multi_energy_filtering and multi_level == "chain":
            try:
                idx, protid = energy_cmap(index=idx, numbering=numbering, res_names=res_names, protid=protid,
                                            potential_sign=multi_energy_mode)
            except IndexError:
                print(
                    f"There is no contact map for {multi_obj} that can satisfy the provided energy filtering. Skipping...")
        if multi_len_filtering and multi_level == "chain":
            try:
                idx = length_filter(index=idx, distance=multi_filtering_dist, mode=multi_filter_mode)
            except IndexError:
                print(
                    f"There is no contact map for {multi_obj} that can satisfy the provided length filtering. Skipping...")

        if multi_level == "chain":
            mat, psc = get_matrix(index=idx, protid=protid)
            p.append(psc[1])
            s.append(psc[2])
            x.append(psc[3])
            psclist.append(psc)
        else:
            mat, multi_stats, multi_chain_stats = get_matrix(index=idx, protid=protid)
            adj_psc = [multi_stats[0], multi_stats[1], multi_stats[2], multi_stats[3]]
            p.append(multi_stats[1])
            s.append(multi_stats[2])
            x.append(multi_stats[3])
            adj_psc.append({'I2': multi_stats[4], 'I3': multi_stats[5], 'I4': multi_stats[6]})
            adj_psc.append({'T2': multi_stats[7], 'T3': multi_stats[8]})
            adj_psc.append({'L': multi_stats[-1]})
            psclist.append(adj_psc)

        entangled = get_stats(mat)

        if multi_circuit_plot:
            circuit_plot(index=idx, protid=protid, numbering=numbering)
        if multi_matrix_plot:
            if multi_level == "chain":
                matrix_plot(mat=mat, protid=protid)
            else:
                matrix_plot_model(mat=mat, protid=protid)
                
        if multi_stats_plot:
            if multi_level == "chain":
                stats_plot(entangled, psc, protid)
            else:
                stats_plot(entangled, multi_stats, protid)

        if multi_export_cmap3:
            for c in multi_obj_chains:
                temp_multi = f"{multi_obj}_chain_{c}_exp.pdb"
                cmd.save(temp_multi, f"{multi_obj} and chain {c}", state=cmd.get_state())
                temp_multi_fpath = os.path.abspath(temp_multi)
                curr_multi_chain, _ = retrieve_chain(temp_multi_fpath)
                temp_i, temp_num, _, res_names = get_cmap(curr_multi_chain, cutoff_distance=cutoff_dist_multi,
                                                            cutoff_numcontacts=multi_num_contacts,
                                                            exclude_neighbour=multi_neighbours)
                temp_multi_f_base = os.path.splitext(os.path.basename(temp_multi_fpath))[0]
                export_cmap3(temp_i, temp_multi_f_base, temp_num, output_dir)
                if os.path.exists(temp_multi):
                    os.remove(temp_multi_fpath)

        if multi_export_mat:
            export_mat(idx, mat, multi_obj, output_dir)

        cmd.delete(multi_obj)

    if multi_psc:
        export_psc(psclist, output_dir)
    if multi_plot_psc:
        plt.rcParams.update({'font.size': 14})
        time = range(len(p))
        plt.plot(time, p, label="P", color="red", linewidth=1.5)
        plt.plot(time, s, label="S", color="green", linewidth=1.5)
        plt.plot(time, x, label="X", color="blue", linewidth=1.5)
        plt.xlabel("Frame #")
        plt.ylabel("Number of contacts")
        plt.legend()
        plt.title(f"P,S,X contacts over {len(p)} frames")
        plt.show()
