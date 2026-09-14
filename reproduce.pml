# ===========================================================================
#  reproduce.pml - Protein Circuit Topology reproduction script
#
#  Headless:
#      pymol -cqy reproduce.pml
#  In PyMOL:
#      @reproduce.pml
#
#  Runs the analysis pipeline through the plugin's REGISTERED PyMOL commands
#  on the bundled structures (1AKI, 1CRN, 1UBQ), writes the CSVs, compares
#  them against the committed reference outputs, colours each structure by
#  its Cross-relation participation, saves a ray-traced image and a .pse
#  session, and writes the figures of the SoftwareX paper (1AKI) with large
#  fonts to <CT_OUTDIR>/figures/paper/.
#
#  Contact criterion: 4.5 A, at least 5 atom-atom pairs, |i - j| > 3 residues,
#  heavy atoms only (the plugin's default; include_hydrogens=False).
#
#  Exit codes
#      0  everything reproduced
#      1  an assertion failed or an error was raised
#      2  an expected output file was not produced
#      4  the plugin source tree could not be located
#
#  Environment
#      CT_REPO    plugin source root  (default, workspace)
#      CT_OUTDIR  output folder       (default, ./reproduce_out)
# ===========================================================================

# Prepare and test function imports
python
import os
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
except Exception:
    pass

from pymol import cmd


def fail(code, message):
    """Print, flush, then exit with a code the shell can actually see."""
    print(f"[reproduce] FAIL: {message}")
    sys.stdout.flush()
    sys.stderr.flush()
    cmd.quit(code)


_script = globals().get("__script__")
if os.environ.get("CT_REPO"):
    REPO = Path(os.environ["CT_REPO"]).resolve()
elif _script:
    REPO = Path(_script).resolve().parent
else:
    REPO = Path.cwd()

if not (REPO / "initialization_checks.py").is_file():
    fail(4, f"no plugin source at {REPO}. Run from the repository root or set CT_REPO.")

OUTDIR = Path(os.environ.get("CT_OUTDIR") or (Path.cwd() / "reproduce_out")).resolve()
FIGDIR = OUTDIR / "figures"
CSVDIR = OUTDIR / "csv"
PAPERDIR = FIGDIR / "paper"
for _d in (OUTDIR, FIGDIR, CSVDIR, PAPERDIR):
    _d.mkdir(parents=True, exist_ok=True)

INPUTS = REPO / "tests" / "data" / "inputs"

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["MPLBACKEND"] = "Agg"
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.image as mimg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.cm import ScalarMappable
from matplotlib.colors import to_rgb

from functions.plots._palette import VIEWER_CONTACT_COLORS, discrete_cmap
from initialization_checks import register_pymol_functions
from utils.config import CONTACT_MAP
from utils.relations import _shade_fraction

register_pymol_functions()

NEEDED = (
    "retrieve_chain", "get_cmap", "get_matrix", "get_stats", "local_ct",
    "get_relation_type_vector", "color_by_relation", "get_folding_score",
    "circuit_plot", "matrix_plot", "stats_plot", "local_topology_plot",
    "export_cmap3", "export_mat", "export_psx",
)
_absent = [n for n in NEEDED if n not in cmd.keyword]
if _absent:
    fail(1, f"commands not registered: {_absent}")
K = {n: cmd.keyword[n][0] for n in NEEDED}

print(f"[reproduce] source  {REPO}")
print(f"[reproduce] output  {OUTDIR}")
print(f"[reproduce] {len(cmd.keyword)} PyMOL keywords registered")

PARAMS = dict(cutoff_distance=4.5, cutoff_numcontacts=5, exclude_neighbour=3, include_hydrogens=False)
print(f"[reproduce] contact criterion {PARAMS} (heavy atoms only)")
# Alphabetical, because the Multi-File tab walks a directory in sorted order and
# psxresults.csv is compared row for row against tests/data/expected/multi/.
CASES = ("1aki", "1crn", "1ubq")
RELATION_TYPES = ("P", "S", "X")

PAPER = "1aki"
PAPER_RESIDUE = 1
PAPER_DPI = 300
RAY_W, RAY_H = 1800, 1400
# Fonts only.
PAPER_RC = {
    "font.size": 16, "axes.titlesize": 18, "axes.labelsize": 16,
    "xtick.labelsize": 14, "ytick.labelsize": 14, "legend.fontsize": 14,
}

psx_rows = []
folding_scores = {}
topology_data = {}
python end

# Test analysis
python
for stem in CASES:
    pdb = INPUTS / f"{stem}.pdb"
    if not pdb.is_file():
        fail(2, f"missing input {pdb}")

    cmd.load(str(pdb), stem)
    cmd.remove(f"{stem} and not polymer")

    chain, protid = K["retrieve_chain"](pdb)
    idx, numbering, protid, res_names = K["get_cmap"](chain, level="chain", **PARAMS)
    if len(idx) == 0:
        fail(1, f"{stem}: no contacts found")
    mat, psx, _ = K["get_matrix"](idx, protid)
    psx_rows.append(psx)
    print(f"[reproduce] {protid}: {len(idx)} contacts, P={psx[1]} S={psx[2]} X={psx[3]}")

    K["export_cmap3"](idx, f"{stem}_chain_A", numbering, CSVDIR)
    K["export_mat"](idx, mat, stem, CSVDIR)

    score = K["get_folding_score"](mat, idx, numbering)
    folding_scores[protid] = float(score)
    print(f"[reproduce] {protid}: CT folding score {score:.4f}")

    for label in ("circuit_plot", "matrix_plot", "stats_plot"):
        plt.close("all")
        if label == "circuit_plot":
            K[label](index=idx, protid=protid, numbering=numbering)
        elif label == "matrix_plot":
            K[label](mat=mat, protid=protid)
        else:
            K[label](K["get_stats"](mat), psx, protid)
        figs = plt.get_fignums()
        if not figs:
            fail(2, f"{label} produced no figure for {stem}")
        out = FIGDIR / f"{stem}_{label}.png"
        plt.gcf().savefig(out, dpi=150, bbox_inches="tight", metadata={"Software": None})
        plt.close("all")
        if not out.is_file() or out.stat().st_size < 5000:
            fail(2, f"{out.name} was not written or is too small")

    topology_data[stem] = (mat, idx, numbering)

K["export_psx"](psx_rows, CSVDIR)
if not (CSVDIR / "psxresults.csv").is_file():
    fail(2, "psxresults.csv was not written")
python end

# Produce visual output
hide everything
show cartoon
set cartoon_transparency, 0.1
bg_color white
set ray_opaque_background, 1
orient
zoom complete=1
viewport 900, 700

python
cmd.set("max_threads", 1)
for rtype in RELATION_TYPES:
    for stem, (mat, idx, numbering) in topology_data.items():
        vec = K["get_relation_type_vector"](mat, idx, rtype, numbering)
        if vec is None:
            fail(1, f"{stem}: no relation type vector for {rtype}")
        K["color_by_relation"](molecule_name=stem, relation_vector=vec,
                               numbering=numbering, relation_type=rtype)
    cmd.ray(900, 700)
    cmd.png(str(FIGDIR / f"relation_type_cartoon_{rtype}.png"), dpi=150)
cmd.save(str(OUTDIR / "session.pse"))
python end

# Paper figures (1AKI).
python
mat, idx, numbering = topology_data[PAPER]
psx = psx_rows[CASES.index(PAPER)]
protid = psx[0]
paper_files = []


def save_paper(name):
    out = PAPERDIR / name
    plt.gcf().savefig(out, dpi=PAPER_DPI, bbox_inches="tight", metadata={"Software": None})
    plt.close("all")
    paper_files.append(out)
    return out

RELATIONS = {code: label for label, code in CONTACT_MAP.items()}

with plt.rc_context(PAPER_RC):
    hits = np.where(np.asarray(numbering) == PAPER_RESIDUE)[0]
    if hits.size == 0:
        fail(1, f"{protid}: residue {PAPER_RESIDUE} not found")
    siteid = int(hits[0])
    counts = K["local_ct"](idx, mat, numbering)[siteid]
    print(f"[reproduce] {protid}: residue {PAPER_RESIDUE} is list position {siteid}; local CT {counts}")

    panels = []
    for code, title in RELATIONS.items():
        plt.close("all")
        K["local_topology_plot"](idx, mat, numbering, siteid, code)
        if not plt.gcf().get_axes():
            fail(2, f"local_topology_plot drew nothing for {code}")
        plt.gca().set_title(title)
        panels.append(save_paper(f"fig3_lct_{PAPER}_res{PAPER_RESIDUE}_{code}.png"))

    images = [mimg.imread(str(p)) for p in panels]
    h, w = images[0].shape[:2]
    fig, axes = plt.subplots(2, 2, figsize=(2 * w / PAPER_DPI, 2 * h / PAPER_DPI))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0.02, hspace=0.02)
    for ax, img in zip(axes.flat, images):
        ax.imshow(img)
        ax.axis("off")
    save_paper(f"fig3_lct_{PAPER}_res{PAPER_RESIDUE}.png")

    plt.close("all")
    K["matrix_plot"](mat=mat, protid=protid)
    save_paper(f"fig4a_matrix_{PAPER}.png")
    plt.close("all")
    K["circuit_plot"](index=idx, protid=protid, numbering=numbering)
    save_paper(f"fig4b_circuit_{PAPER}.png")
    plt.close("all")
    K["stats_plot"](K["get_stats"](mat), psx, protid)
    save_paper(f"fig7_stats_{PAPER}.png")

    cmd.disable("all")
    cmd.enable(PAPER)
    cmd.orient(PAPER)
    cmd.zoom(PAPER, complete=1)
    for rtype, name in (("S", "Series (S)"), ("P", "Parallel (P)"), ("X", "Cross (X)")):
        vec = K["get_relation_type_vector"](mat, idx, rtype, numbering)
        bounds = K["color_by_relation"](molecule_name=PAPER, relation_vector=vec,
                                        numbering=numbering, relation_type=rtype)
        if not bounds:
            fail(1, f"{protid}: no colour levels for {rtype}")
        print(f"[reproduce] {protid}: {rtype} per-residue max {int(vec.max())}, "
              f"colour levels {[int(b) for b in bounds]}")
        render = PAPERDIR / f"fig5_cartoon_{PAPER}_{rtype}_render.png"
        cmd.ray(RAY_W, RAY_H)
        cmd.png(str(render), dpi=PAPER_DPI)
        if not render.is_file():
            fail(2, f"{render.name} was not written")

        rgb = np.asarray(to_rgb(VIEWER_CONTACT_COLORS[rtype]))
        cells = ["white"] + [tuple(1 - _shade_fraction(k, len(bounds)) * (1 - rgb))
                             for k in range(1, len(bounds) + 1)]
        cmap, norm = discrete_cmap(cells)

        fig = plt.figure(figsize=(7.7, 5.25))
        ax = fig.add_axes([0, 0, 0.86, 1])
        ax.imshow(mimg.imread(str(render)))
        ax.axis("off")
        cax = fig.add_axes([0.885, 0.12, 0.035, 0.76])
        cbar = fig.colorbar(ScalarMappable(norm=norm, cmap=cmap), cax=cax,
                            ticks=range(1, len(bounds) + 2), spacing="uniform")
        cbar.ax.set_yticklabels(["0", *[str(int(b)) for b in bounds]])
        cbar.ax.tick_params(length=0, labelsize=20)
        cbar.set_label(f"{name} relations per residue", fontsize=20)
        save_paper(f"fig5_cartoon_{PAPER}_{rtype}.png")
    cmd.enable("all")
python end

# Verify and report
python
expected = [
    CSVDIR / "psxresults.csv",
    OUTDIR / "session.pse",
]
expected += [FIGDIR / f"relation_type_cartoon_{t}.png" for t in RELATION_TYPES]
for stem in CASES:
    expected += [
        CSVDIR / f"{stem}_chain_A_cmap3.csv",
        CSVDIR / f"{stem}_mat.csv",
        FIGDIR / f"{stem}_circuit_plot.png",
        FIGDIR / f"{stem}_matrix_plot.png",
        FIGDIR / f"{stem}_stats_plot.png",
    ]
expected += paper_files

missing = [str(p) for p in expected if not p.is_file()]
if missing:
    fail(2, f"{len(missing)} expected output(s) missing: {missing}")
small = [p.name for p in paper_files if p.stat().st_size < 5000]
if small:
    fail(2, f"paper figure(s) too small to be real: {small}")

# Compare
REFERENCES = {
    "1aki_chain_A_cmap3.csv": "single_1aki/1aki_chain_A_cmap3.csv",
    "1aki_mat.csv":           "single_1aki/1aki_mat.csv",
    "1crn_chain_A_cmap3.csv": "single_1crn/1crn_chain_A_cmap3.csv",
    "1crn_mat.csv":           "single_1crn/1crn_mat.csv",
    "1ubq_chain_A_cmap3.csv": "single_1ubq/1ubq_chain_A_cmap3.csv",
    "1ubq_mat.csv":           "single_1ubq/1ubq_mat.csv",
    "psxresults.csv":         "multi/psxresults.csv",
}
EXPECTED_DIR = REPO / "tests" / "data" / "expected"

if not EXPECTED_DIR.is_dir():
    fail(2, f"no reference outputs at {EXPECTED_DIR}")

def _norm(path):
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")

mismatched = []
for produced_name, reference_rel in REFERENCES.items():
    produced, reference = CSVDIR / produced_name, EXPECTED_DIR / reference_rel
    if not reference.is_file():
        fail(2, f"missing reference file {reference}")
    got, want = _norm(produced), _norm(reference)
    if got == want:
        print(f"[reproduce]   {produced_name}: matches the committed reference")
        continue
    got_lines, want_lines = got.splitlines(), want.splitlines()
    detail = f"{len(got_lines)} lines vs {len(want_lines)} expected"
    for n, (a, b) in enumerate(zip(got_lines, want_lines), 1):
        if a != b:
            detail = f"first difference at line {n}"
            break
    mismatched.append(f"{produced_name} ({detail})")

if mismatched:
    fail(1, f"{len(mismatched)} output(s) differ from the committed reference: {mismatched}")

# The CT Folding Score is not written to any CSV, so it is pinned here.
EXPECTED_FOLDING = {"1aki_A": 283.255814, "1crn_A": 77.043478, "1ubq_A": 127.578947}
for protid, want_score in EXPECTED_FOLDING.items():
    got_score = folding_scores.get(protid)
    if got_score is None:
        fail(1, f"no folding score was computed for {protid}")
    if abs(got_score - want_score) > 1e-6:
        fail(1, f"{protid}: folding score {got_score:.6f}, expected {want_score:.6f}")
    print(f"[reproduce]   {protid}: CT folding score {got_score:.6f} matches")

print(f"[reproduce] OK - {len(expected)} artefacts in {OUTDIR}")
for p in sorted(expected):
    print(f"[reproduce]   {p.relative_to(OUTDIR)}  ({p.stat().st_size} bytes)")
sys.stdout.flush()
python end
