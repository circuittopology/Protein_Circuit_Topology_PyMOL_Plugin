"""
Configuration file for UI stylesheets and constants.
"""

SECTION_STYLESHEET = """QGroupBox {font-weight: bold; border: 1px solid palette(dark); border-radius: 6px; margin-top: 6px; padding-top: 4px;}
QGroupBox::title {subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px;}"""

INFO_BUTTON_STYLE = "QPushButton { border: none; color: gray; }"

WARN_MSG = (
    "Please use the 'Remove Non-Polymer Atoms' button to remove non-polymer atoms, "
    "which can interfere with Circuit Topology."
)
LOCAL_CT_WARN = (
    "To use local Circuit Topology, please select the desired object from the dropdown menu first!"
)
CHECKBOX_WARN = (
    "No checkboxes for plotting or exporting have been ticked!"
)
TRAJECTORY_COLOR_INFO = (
    "Coloring applies to the selected PyMOL object. If that object is a trajectory "
    "(more than one state), this will color EVERY state: the topology analysis is run "
    "for each frame, each frame is colored by its own S/P/X topology, and the frames "
    "are merged into a single multi-state object named '<object>_topo'. "
    "The original object is hidden; delete '<object>_topo' to clean up. "
    "NOTE: For long trajectories this can take a while and use significant memory."
)

CONTACT_MAP = {
    "Series (S)": "S",
    "Parallel (P)": "P",
    "Inverse parallel (IP)": "IP",
    "Cross (X)": "X",
}
