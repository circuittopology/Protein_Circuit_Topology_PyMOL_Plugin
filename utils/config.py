"""
Configuration file for UI stylesheets and constants.
"""

SECTION_STYLESHEET = """QGroupBox {font-weight: bold; border: 1px solid palette(dark); border-radius: 6px; margin-top: 6px; padding-top: 4px;}
QGroupBox::title {subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px;}"""

INFO_BUTTON_STYLE = "QPushButton { border: none; color: gray; }"

NON_POLYMER_NOTE = "Waters, ions and ligands are excluded automatically."

NON_POLYMER_INFO = (
    "Circuit Topology analyses polymer atoms only. Waters, ions, ligands and other non-polymer\n"
    "atoms are excluded automatically at analysis time, and nucleic-acid and UNK residues are\n"
    "dropped when the chain is parsed. Hydrogen atoms are ignored by default so that X-ray, NMR\n"
    "and MD inputs are comparable; tick 'Count hydrogen atoms' in the contact-map parameters for\n"
    "ProteinCT-identical results on hydrogen-bearing files."
)
HYDROGEN_LABEL = "Count hydrogen atoms (ProteinCT-identical)"
HYDROGEN_INFO = (
    "Off (default): only heavy atoms enter the atom-atom contact criterion, so a model with "
    "hydrogens gives the same contacts as the same model without them.\n"
    "On: every atom present is counted, exactly as the reference ProteinCT implementation does. "
    "Hydrogen-bearing files (NMR entries, MD frames) then yield more contacts."
)
LOCAL_CT_WARN = (
    "To use local Circuit Topology, please select the desired object from the dropdown menu first!"
)
CHECKBOX_WARN = (
    "No checkboxes for plotting or exporting have been ticked!"
)
TRAJECTORY_COLOR_INFO = (
    "Coloring applies to the selected PyMOL object. If that object is a trajectory\n"
    "(more than one state), this will color EVERY state: the analysis is run for each\n"
    "frame, each frame is colored by its own participation in S/P/X relations, and the\n"
    "frames are merged into a single multi-state object named '<object>_topo'.\n"
    "The original object is hidden; delete '<object>_topo' to clean up.\n"
    "NOTE: For long trajectories this can take a while and use significant memory."
)

CONTACT_MAP = {
    "Series (S)": "S",
    "Parallel (P)": "P",
    "Inverse parallel (IP)": "IP",
    "Cross (X)": "X",
}

LENGTH_FILTER_MODES = {
    "equality (=)": "=",
    "less than (<)": "<",
    "greater than (>)": ">",
}

ENERGY_FILTER_MODES = {
    "Attractive / stabilising (+)": "+",
    "Repulsive / destabilising (−)": "-",  # noqa: RUF001
}
