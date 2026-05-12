import logging
import tempfile
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from pymol import cmd
from PyQt5.QtWidgets import QMessageBox

from functions.calculating.energy_cmap import energy_cmap
from functions.calculating.get_cmap import get_cmap
from functions.calculating.get_matrix import get_matrix
from functions.calculating.get_stats import get_stats
from functions.calculating.length_filter import length_filter
from functions.exporting.export_cmap3 import export_cmap3
from functions.exporting.export_mat import export_mat
from functions.exporting.export_psc import export_psc
from functions.importing.retrieve_chain import retrieve_chain
from functions.plots.circuit_plot import circuit_plot
from functions.plots.matrix_plot import matrix_plot
from functions.plots.matrix_plot_model import matrix_plot_model
from functions.plots.stats_plot import stats_plot
from utils.config import CHECKBOX_WARN, WARN_MSG
from utils.helpers import resolve_output_path
from utils.non_polymer import has_non_polymer_atoms

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Slight rewrite to match their notebook code because we had bugs
def run_multi_analysis(self: Any) -> None:  # noqa: PLR0912, PLR0915
    """
    Runs the multi-file circuit topology analysis.
    Iterates through files in the selected directory, performs analysis, and generates plots/exports.

    Args:
        self: The main GUI class instance.
    """
    # check for non-polymer atoms
    if has_non_polymer_atoms():
        QMessageBox.warning(self, "Warning", WARN_MSG)

    vals = self.get_multiple_values()
    # Yes/No options (retrieving once rather than every time in for loop)
    multi_energy_filtering = vals["energy_filtering"]
    multi_len_filtering = vals["length_filtering"]
    multi_circuit_plot = vals["circuit_plot"]
    multi_matrix_plot = vals["matrix_plot"]
    multi_stats_plot = vals["stats_plot"]
    multi_export_cmap3 = vals["export_cmap3"]
    multi_export_psc = vals["export_psc"]
    multi_export_mat = vals["export_mat"]
    multi_input_dir = vals["directory"]
    multi_traj_dir = vals["traj_directory"]
    multi_plot_psc = vals["plot_psc"]
    if not multi_input_dir and not multi_traj_dir:
        QMessageBox.warning(self, "Error", "No input directory selected!")
        return

    path = Path(multi_traj_dir or multi_input_dir)

    if not path.exists():
        QMessageBox.warning(self, "Error", f"The input directory does not exist: {path}")
        return

    output_dir = vals["output_directory"]

    if not output_dir and (multi_export_cmap3 or multi_export_mat or multi_export_psc):
        QMessageBox.warning(self, "Error", f"An output directory has not been selected: {output_dir}")
        return

    output_path = resolve_output_path(self, output_dir)
    if output_path is None:
        return

    number_of_files = len(list(path.iterdir()))
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

    if not (multi_circuit_plot or multi_matrix_plot or multi_stats_plot or multi_export_cmap3 or multi_export_mat or multi_export_psc):
        QMessageBox.warning(self, "Error", CHECKBOX_WARN)
        return

    if multi_circuit_plot or multi_matrix_plot or multi_stats_plot or multi_export_cmap3 or multi_export_mat:
        confirm = QMessageBox.question(self,
                                        "Continue multi-file analysis",
                                        f"Are you sure you want to continue with multi-file analysis?\n\nIt will create a plot / export a .csv for each of your {number_of_files} files!",
                                        QMessageBox.Yes | QMessageBox.No)

        if confirm != QMessageBox.Yes:
            logger.info("Multi-file analysis was aborted.")
            return

    for num, files in enumerate(path.iterdir()):
        if files.suffix in (".pdb", ".cif"):
            try:
                multi_full_path = files
                multi_obj = files.stem
                cmd.load(str(multi_full_path), multi_obj)
                cmd.remove("not polymer")
                multi_obj_chains = cmd.get_chains(multi_obj)
                multi_chain, protid = retrieve_chain(multi_full_path)
                logger.info("%s - %d/%d", files, num + 1, number_of_files)
            except Exception:
                logger.exception("%s", files)
                continue
        else:
            continue

        if len(multi_obj_chains) > 1:
            multi_level = "model"
            logger.info("The object %s has multiple chains. Performing multi-chain CT analysis...", multi_obj)
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
                logger.warning("There is no contact map for %s that can satisfy the provided energy filtering. Skipping...", multi_obj)
        if multi_len_filtering and multi_level == "chain":
            try:
                idx = length_filter(index=idx, distance=multi_filtering_dist, mode=multi_filter_mode)
            except IndexError:
                logger.warning("There is no contact map for %s that can satisfy the provided length filtering. Skipping...", multi_obj)

        if multi_level == "chain":
            mat, psc_result, _ = get_matrix(index=idx, protid=protid)
            p.append(psc_result[1])
            s.append(psc_result[2])
            x.append(psc_result[3])
            psclist.append(psc_result)
        else:
            mat, psc_result, _ = get_matrix(index=idx, protid=protid)
            adj_psc = [psc_result[0], psc_result[1], psc_result[2], psc_result[3]]
            p.append(psc_result[1])
            s.append(psc_result[2])
            x.append(psc_result[3])
            adj_psc.append({"I2": psc_result[4], "I3": psc_result[5], "I4": psc_result[6]})
            adj_psc.append({"T2": psc_result[7], "T3": psc_result[8]})
            adj_psc.append({"L": psc_result[-1]})
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
                stats_plot(entangled, psc_result, protid)
            else:
                stats_plot(entangled, psc_result, protid)

        if multi_export_cmap3:
            for c in multi_obj_chains:
                with tempfile.NamedTemporaryFile(suffix=".pdb", delete=False) as tmp:
                    tmp_path = Path(tmp.name)
                cmd.save(tmp_path, f"{multi_obj} and chain {c}", state=cmd.get_state())
                try:
                    curr_multi_chain, _ = retrieve_chain(tmp_path)
                    temp_i, temp_num, _, res_names = get_cmap(curr_multi_chain, cutoff_distance=cutoff_dist_multi,
                                                                cutoff_numcontacts=multi_num_contacts,
                                                                exclude_neighbour=multi_neighbours)
                    temp_multi_f_base = f"{multi_obj}_chain_{c}"
                    export_cmap3(temp_i, temp_multi_f_base, temp_num, output_path)
                finally:
                    if tmp_path.exists():
                        tmp_path.unlink()

        if multi_export_mat:
            export_mat(idx, mat, multi_obj, output_path)

        cmd.delete(multi_obj)

    if multi_export_psc:
        export_psc(psclist, output_path)
    if multi_plot_psc:
        plt.rcParams.update({"font.size": 14})
        time = range(len(p))
        plt.plot(time, p, label="P", color="red", linewidth=1.5)
        plt.plot(time, s, label="S", color="green", linewidth=1.5)
        plt.plot(time, x, label="X", color="blue", linewidth=1.5)
        plt.xlabel("Frame #")
        plt.ylabel("Number of contacts")
        plt.legend()
        plt.title(f"P,S,X contacts over {len(p)} frames")
        plt.show()
