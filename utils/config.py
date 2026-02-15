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

CONTACT_MAP = {
    "Series (S)": "S",
    "Parallel (P)": "P",
    "Inverse parallel (P-)": "IP",
}
