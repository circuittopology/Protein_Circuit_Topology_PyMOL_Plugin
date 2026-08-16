# ===========================================================================
#  reproduce.pml - Protein Circuit Topology reproduction script
#
#  Headless:
#      pymol -cqy reproduce.pml
#  In PyMOL:
#      @reproduce.pml
#
#  Runs the analysis pipeline through the plugin's REGISTERED PyMOL commands,
#  writes the CSVs, colours each structure by cross-contact density,
#  and saves a ray-traced image and a .pse session.
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
for _d in (OUTDIR, FIGDIR, CSVDIR):
    _d.mkdir(parents=True, exist_ok=True)

INPUTS = REPO / "tests" / "data" / "inputs"

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["MPLBACKEND"] = "Agg"
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt

from initialization_checks import register_pymol_functions

register_pymol_functions()

NEEDED = (
    "retrieve_chain", "get_cmap", "get_matrix", "get_stats",
    "get_topology_vector", "color_by_topology", "get_folding_score",
    "circuit_plot", "matrix_plot", "stats_plot",
    "export_cmap3", "export_mat", "export_psx",
)
_absent = [n for n in NEEDED if n not in cmd.keyword]
if _absent:
    fail(1, f"commands not registered: {_absent}")
K = {n: cmd.keyword[n][0] for n in NEEDED}

print(f"[reproduce] source  {REPO}")
print(f"[reproduce] output  {OUTDIR}")
print(f"[reproduce] {len(cmd.keyword)} PyMOL keywords registered")

PARAMS = dict(cutoff_distance=4.5, cutoff_numcontacts=5, exclude_neighbour=3)
CASES = ("1crn", "1ubq")
TOPOLOGY_TYPES = ("P", "S", "X")
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
for ttype in TOPOLOGY_TYPES:
    for stem, (mat, idx, numbering) in topology_data.items():
        vec = K["get_topology_vector"](mat, idx, ttype, numbering)
        if vec is None:
            fail(1, f"{stem}: no topology vector for {ttype}")
        K["color_by_topology"](molecule_name=stem, topology_vector=vec,
                               numbering=numbering, topology_type=ttype)
    cmd.ray(900, 700)
    cmd.png(str(FIGDIR / f"topology_cartoon_{ttype}.png"), dpi=150)
cmd.save(str(OUTDIR / "session.pse"))
python end

# Verify and report
python
expected = [
    CSVDIR / "psxresults.csv",
    OUTDIR / "session.pse",
]
expected += [FIGDIR / f"topology_cartoon_{t}.png" for t in TOPOLOGY_TYPES]
for stem in CASES:
    expected += [
        CSVDIR / f"{stem}_chain_A_cmap3.csv",
        CSVDIR / f"{stem}_mat.csv",
        FIGDIR / f"{stem}_circuit_plot.png",
        FIGDIR / f"{stem}_matrix_plot.png",
        FIGDIR / f"{stem}_stats_plot.png",
    ]

missing = [str(p) for p in expected if not p.is_file()]
if missing:
    fail(2, f"{len(missing)} expected output(s) missing: {missing}")

# Compare
REFERENCES = {
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
EXPECTED_FOLDING = {"1crn_A": 77.043478, "1ubq_A": 127.578947}
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
