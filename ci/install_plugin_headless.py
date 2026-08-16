"""
Install the release ZIP into a PyMOL installation through PyMOL's own Plugin Manager.

Usage:
    python ci/install_plugin_headless.py <plugin.zip> <plugin-dir>

Exit codes: 0 installed and all commands registered | 1 install or verification failed | 2 bad usage.
"""
from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path

EXPECTED_COMMANDS = (
    "circuit_plot", "matrix_plot", "stats_plot", "matrix_plot_model", "local_topology_plot",
    "get_cmap", "get_matrix", "get_stats", "energy_cmap", "length_filter", "local_ct",
    "retrieve_chain", "export_psx", "export_cmap3", "export_mat",
    "get_topology_vector", "color_by_topology", "get_folding_score",
)

_ANSWERS = {
    "showinfo": None, "showwarning": None, "showerror": None,
    "askyesno": True, "askokcancel": True, "askretrycancel": False,
}


class _HeadlessDialogs:
    """Answers PyMOL's installer prompts instead of opening a real dialog."""
    def __init__(self) -> None:
        self.messages: list[tuple[str, str, str]] = []

    def __getattr__(self, name: str):
        if name not in _ANSWERS:
            raise AttributeError(name)

        def answer(title="", message="", **_kw):
            self.messages.append((name, str(title), str(message)))
            return _ANSWERS[name]

        return answer


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)

        return 2

    zip_path = Path(argv[1]).resolve()
    plugdir = Path(argv[2]).resolve()

    if not zip_path.is_file():
        print(f"FAIL: no such ZIP: {zip_path}")

        return 2

    plugdir.mkdir(parents=True, exist_ok=True)

    import pymol

    pymol.finish_launching(["pymol", "-qc"])

    import pmg_qt.mimic_tk  # noqa: F401
    from pymol import cmd
    from pymol.plugins import installation

    answers = _HeadlessDialogs()
    sys.modules["tkMessageBox"] = answers

    print(f"installing {zip_path.name} into {plugdir}")

    try:
        installation.installPluginFromFile(str(zip_path), parent=None, plugdir=str(plugdir))
    except Exception:
        print("FAIL: installPluginFromFile raised")
        traceback.print_exc()

        return 1

    for kind, title, message in answers.messages:
        print(f"  [{kind}] {title}: {message}")

    if any(kind == "showerror" or title.lower().startswith("error")
           for kind, title, _ in answers.messages):
        print("FAIL: the installer reported an error")

        return 1

    tk_loaded = sorted(m for m in sys.modules if m == "tkinter" or m.startswith("tkinter."))
    if tk_loaded:
        print(f"FAIL: Tk was loaded ({tk_loaded}); the dialog layer left Qt")

        return 1

    installed = sorted(p.name for p in plugdir.iterdir())

    print(f"plugin dir now contains: {installed}")

    if not installed:
        print("FAIL: nothing was installed")

        return 1

    name = installed[0]

    missing = [c for c in EXPECTED_COMMANDS if c not in cmd.keyword]
    if missing:
        print(f"FAIL: {len(missing)} command(s) missing from cmd.keyword: {missing}")

        return 1

    print(f"OK: installed {name!r} and all {len(EXPECTED_COMMANDS)} commands registered")
    return 0


if __name__ == "__main__":
    rc = main(sys.argv)

    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(rc)
