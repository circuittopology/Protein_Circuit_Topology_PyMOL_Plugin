import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from pymol import cmd
from PyQt5.QtWidgets import QMessageBox

from functions.calculating.energy_cmap import energy_cmap
from functions.calculating.get_cmap import get_cmap
from functions.calculating.get_matrix import get_matrix
from functions.calculating.get_stats import get_stats
from functions.calculating.length_filter import length_filter
from functions.exporting.export_cmap3 import export_cmap3
from functions.exporting.export_mat import export_mat
from functions.exporting.export_psx import export_psx
from functions.importing.retrieve_chain import retrieve_chain
from functions.plots._palette import CONTACT_COLORS
from functions.plots.circuit_plot import circuit_plot
from functions.plots.matrix_plot import matrix_plot
from functions.plots.matrix_plot_model import matrix_plot_model
from functions.plots.stats_plot import stats_plot
from utils.config import CHECKBOX_WARN
from utils.helpers import resolve_output_path, temp_pdb_export
from utils.validation import (
    chain_selection,
    count_object_states,
    get_object_chains,
    legalize_object_name,
    list_structure_files,
    object_exists,
    polymer_selection,
    selection_has_atoms,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# How many structure names to spell out before summarising the rest.
_MAX_LISTED = 5


@dataclass(frozen=True)
class _WorkItem:
    """
    One unit of analysis, whether it came from a file or from a trajectory state.

    label  what it is called in messages and in exported filenames.
    obj    the PyMOL object to take chain selections from.
    state  which coordinate state to read.
    path   the file to parse.
    """
    label: str
    obj: str
    state: int
    path: Path | None = None


def _states_of(traj_obj: str, n_states: int) -> list[_WorkItem]:
    """One work item per trajectory state, read straight from the loaded object."""
    width = len(str(n_states))
    return [
        _WorkItem(label=f"{traj_obj}_frame_{state:0{width}d}", obj=traj_obj, state=state)
        for state in range(1, n_states + 1)
    ]

# Slight rewrite to match their notebook code because we had bugs
def run_multi_analysis(self: Any) -> None:  # noqa: PLR0911, PLR0912, PLR0915
    """
    Runs the multi-file circuit topology analysis.
    Iterates through files in the selected directory, performs analysis, and generates plots/exports.

    Args:
        self: The main GUI class instance.
    """
    vals = self.get_multiple_values()
    multi_energy_filtering = vals["energy_filtering"]
    multi_len_filtering = vals["length_filtering"]
    multi_circuit_plot = vals["circuit_plot"]
    multi_matrix_plot = vals["matrix_plot"]
    multi_stats_plot = vals["stats_plot"]
    multi_export_cmap3 = vals["export_cmap3"]
    multi_export_psx = vals["export_psx"]
    multi_export_mat = vals["export_mat"]
    multi_input_dir = vals["directory"]
    multi_traj_dir = vals["traj_directory"]
    multi_plot_psx = vals["plot_psx"]

    if not (multi_circuit_plot or multi_matrix_plot or multi_stats_plot or multi_export_cmap3 or multi_export_mat or multi_export_psx):
        QMessageBox.warning(self, "Error", CHECKBOX_WARN)
        return

    traj_obj = vals.get("trajectory_object")
    traj_states = count_object_states(traj_obj) if traj_obj else 0

    if traj_states > 1:
        items = _states_of(traj_obj, traj_states)
    else:
        if not multi_input_dir and not multi_traj_dir:
            QMessageBox.warning(self, "Error", "No input directory or loaded trajectory to analyse!")
            return

        path = Path(multi_traj_dir or multi_input_dir)
        try:
            input_files = list_structure_files(path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to read input directory:\n{e}")
            return

        if not input_files:
            QMessageBox.warning(self, "Error",
                f"No PDB or CIF files found in the selected directory: {path}."
                f" If you are trying to analyse a trajectory, load it with a PDB/CIF first - "
                f"converting it to separate files is not required.",
            )
            return
        items = [_WorkItem(label=legalize_object_name(f.stem), obj=legalize_object_name(f.stem),
                           state=1, path=f) for f in input_files]

    output_dir = vals["output_directory"]
    output_path = None
    if multi_export_cmap3 or multi_export_mat or multi_export_psx:
        output_path = resolve_output_path(self, output_dir)
        if output_path is None:
            return

    number_of_files = len(items)
    psxlist = []
    p = []
    s = []
    x = []
    processed_count = 0
    skipped_count = 0
    skipped_filters: list[tuple[str, list[str]]] = []

    cutoff_dist_multi = vals["cutoff_distance"]
    multi_neighbours = vals["exclude_neighbour"]
    multi_num_contacts = vals["cutoff_numcontacts"]
    multi_energy_mode = vals["energy_filtering_mode"]
    multi_filtering_dist = vals["filtering_distance"]
    multi_filter_mode = vals["length_filter_mode"]

    if multi_circuit_plot or multi_matrix_plot or multi_stats_plot or multi_export_cmap3 or multi_export_mat:
        confirm = QMessageBox.question(self,
                                        "Continue multi-file analysis",
                                        f"Are you sure you want to continue with multi-file analysis?\n\nIt will create a plot / export a .csv for each of your {number_of_files} files!",
                                        QMessageBox.Yes | QMessageBox.No)

        if confirm != QMessageBox.Yes:
            logger.info("Multi-file analysis was aborted.")
            return

    for num, item in enumerate(items, start=1):
        multi_obj = item.obj
        try:
            if item.path is not None:
                cmd.load(str(item.path), multi_obj)
                if not object_exists(multi_obj):
                    msg = f"PyMOL did not create the expected object: {multi_obj}"
                    raise RuntimeError(msg)  # noqa: TRY301
            multi_obj_chains = get_object_chains(multi_obj)
            if not multi_obj_chains:
                msg = "No protein chains were found after loading."
                raise ValueError(msg)  # noqa: TRY301

            if item.path is not None:
                multi_chain, protid = retrieve_chain(item.path)
            else:
                with temp_pdb_export(
                    polymer_selection(multi_obj), state=item.state, label=item.label,
                ) as tmp_path:
                    multi_chain, protid = retrieve_chain(tmp_path)
            logger.info("%s - %d/%d", item.label, num, number_of_files)

            if len(multi_obj_chains) > 1:
                multi_level = "model"
                logger.info("The object %s has multiple chains. Performing multi-chain CT analysis...", multi_obj)
            else:
                multi_level = "chain"

            idx, numbering, protid, res_names = get_cmap(
                multi_chain,
                level=multi_level,
                cutoff_distance=cutoff_dist_multi,
                cutoff_numcontacts=multi_num_contacts,
                exclude_neighbour=multi_neighbours,
            )
            if idx.size == 0:
                skipped_count += 1
                continue

            if multi_level != "chain" and (multi_energy_filtering or multi_len_filtering):
                requested = [
                    name for name, on in (("energy", multi_energy_filtering), ("length", multi_len_filtering))
                    if on
                ]
                skipped_filters.append((item.label, requested))
                logger.warning(
                    "%s has %d chains, so %s filtering does not apply and was not performed.",
                    multi_obj, len(multi_obj_chains), " and ".join(requested),
                )

            if multi_energy_filtering and multi_level == "chain":
                try:
                    idx, protid = energy_cmap(
                        index=idx,
                        numbering=numbering,
                        res_names=res_names,
                        protid=protid,
                        potential_sign=multi_energy_mode,
                    )
                except Exception:
                    logger.warning("Energy filtering failed for %s", multi_obj, exc_info=True)
                    skipped_count += 1
                    continue
                if idx.size == 0:
                    skipped_count += 1
                    continue

            if multi_len_filtering and multi_level == "chain":
                if multi_filtering_dist is None or multi_filter_mode is None:
                    skipped_count += 1
                    continue
                try:
                    if multi_filter_mode == "=":
                        idx = idx[np.abs(idx[:, 0].astype(int) - idx[:, 1].astype(int)) == int(multi_filtering_dist)]
                    else:
                        idx = length_filter(index=idx, distance=multi_filtering_dist, mode=multi_filter_mode)
                except Exception:
                    logger.warning("Length filtering failed for %s", multi_obj, exc_info=True)
                    skipped_count += 1
                    continue
                if idx.size == 0:
                    skipped_count += 1
                    continue

            mat, psx_result, _ = get_matrix(index=idx, protid=protid)
            if multi_level == "chain":
                p.append(psx_result[1])
                s.append(psx_result[2])
                x.append(psx_result[3])
                psxlist.append(psx_result)
            else:
                adj_psx = [psx_result[0], psx_result[1], psx_result[2], psx_result[3]]
                p.append(psx_result[1])
                s.append(psx_result[2])
                x.append(psx_result[3])
                adj_psx.append({"I2": psx_result[4], "I3": psx_result[5], "I4": psx_result[6]})
                adj_psx.append({"T2": psx_result[7], "T3": psx_result[8]})
                adj_psx.append({"L": psx_result[-1]})
                psxlist.append(adj_psx)

            entangled = get_stats(mat)

            if multi_matrix_plot:
                if multi_level == "chain":
                    matrix_plot(mat=mat, protid=protid)
                else:
                    matrix_plot_model(mat=mat, protid=protid)

            if multi_circuit_plot:
                circuit_plot(index=idx, protid=protid, numbering=numbering)

            if multi_stats_plot:
                stats_plot(entangled, psx_result, protid)

            if multi_export_cmap3:
                if output_path is None:
                    return
                for c in multi_obj_chains:
                    current_selection = chain_selection(multi_obj, c)
                    if not selection_has_atoms(current_selection):
                        logger.warning("Skipping empty chain selection: %s", current_selection)
                        continue
                    with temp_pdb_export(current_selection, state=item.state, label=item.label) as tmp_path:
                        curr_multi_chain, _ = retrieve_chain(tmp_path)
                    temp_i, temp_num, _, _ = get_cmap(
                        curr_multi_chain,
                        cutoff_distance=cutoff_dist_multi,
                        cutoff_numcontacts=multi_num_contacts,
                        exclude_neighbour=multi_neighbours,
                    )
                    if temp_i.size == 0:
                        logger.warning("No contacts found for %s chain %s; skipping contact-map export", multi_obj, c)
                        continue
                    temp_multi_f_base = f"{item.label}_chain_{c}"
                    export_cmap3(temp_i, temp_multi_f_base, temp_num, output_path)
            if multi_export_mat:
                if output_path is None:
                    return
                export_mat(idx, mat, item.label, output_path)

            processed_count += 1
        except Exception:
            logger.exception("Failed processing %s", item.label)
            skipped_count += 1
        finally:
            if item.path is not None and object_exists(multi_obj):
                cmd.delete(multi_obj)

    if multi_export_psx:
        if not psxlist:
            QMessageBox.warning(self, "Warning", "No PSX results were produced, so no PSX CSV was exported.")
        else:
            try:
                if output_path is None:
                    return
                export_psx(psxlist, output_path)
            except Exception as e:
                logger.exception("PSX export failed")
                QMessageBox.warning(self, "Error", f"PSX export failed:\n{e}")
                return

    if multi_plot_psx:
        if not p:
            QMessageBox.warning(self, "Warning", "No PSX results were available to plot.")
        else:
            plt.rcParams.update({"font.size": 14})
            time = range(len(p))
            plt.plot(time, p, label="P", color=CONTACT_COLORS["P"], linewidth=1.5)
            plt.plot(time, s, label="S", color=CONTACT_COLORS["S"], linewidth=1.5)
            plt.plot(time, x, label="X", color=CONTACT_COLORS["X"], linewidth=1.5)
            plt.xlabel("Frame #")
            plt.ylabel("Number of contacts")
            plt.legend()
            plt.title(f"P,S,X contacts over {len(p)} frames")
            plt.show()

    message = f"Processed {processed_count} of {number_of_files} files."
    if skipped_count:
        message += f"\nSkipped {skipped_count} files."

    if skipped_filters:
        listed = ", ".join(f"{name} ({' and '.join(kinds)})" for name, kinds in skipped_filters[:_MAX_LISTED])
        if len(skipped_filters) > _MAX_LISTED:
            listed += f", and {len(skipped_filters) - _MAX_LISTED} more"
        message += (
            f"\n\nFiltering was NOT applied to {len(skipped_filters)} multi-chain structure(s): "
            f"{listed}. Energy and length filtering currently support single-chain objects only."
        )
    QMessageBox.information(self, "Multi-file analysis complete", message)
