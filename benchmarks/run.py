"""Measure wall time and peak memory for the Circuit Topology pipeline."""
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INPUTS = REPO / "tests" / "data" / "inputs"
RESULTS = Path(__file__).resolve().parent / "results.csv"

BASE_PARAMS = {"cutoff_distance": 4.5, "cutoff_numcontacts": 5, "exclude_neighbour": 3}


def peak_rss_mb() -> float:
    """High-water-mark resident set size for this process, in MB."""
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes

        class Counters(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        psapi.GetProcessMemoryInfo.argtypes = [
            wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD,
        ]
        psapi.GetProcessMemoryInfo.restype = wintypes.BOOL

        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        if not psapi.GetProcessMemoryInfo(
            wintypes.HANDLE(-1), ctypes.byref(counters), counters.cb,
        ):
            msg = f"GetProcessMemoryInfo failed (error {ctypes.get_last_error()})"
            raise OSError(msg)
        return counters.PeakWorkingSetSize / 1e6

    import resource

    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # ru_maxrss is kilobytes on Linux and bytes on macOS.
    return peak / 1e3 if sys.platform.startswith("linux") else peak / 1e6


def truncated_pdb(dest: Path, stem: str, n_residues: int | None) -> Path:
    """Keep the first n_residues of a chain, so the length sweep uses real coordinates."""
    lines = (INPUTS / f"{stem}.pdb").read_text().splitlines()
    if n_residues is None:
        dest.write_text("\n".join(lines) + "\n")

        return dest

    kept, seen = [], []

    for line in lines:
        if line.startswith(("ATOM", "HETATM")):
            num = int(line[22:26])
            if num not in seen:
                seen.append(num)
            if len(seen) > n_residues:
                continue
        kept.append(line)

    dest.write_text("\n".join(kept) + "\n")

    return dest


def run_point(spec: dict) -> dict:
    """Time one measurement inside this process and print the result as JSON."""
    import tempfile

    sys.path.insert(0, str(REPO))
    from functions.calculating.get_cmap import get_cmap
    from functions.calculating.get_matrix import get_matrix
    from functions.importing.retrieve_chain import retrieve_chain

    params = dict(BASE_PARAMS, cutoff_distance=spec["cutoff"])
    with tempfile.TemporaryDirectory() as tmp:
        path = truncated_pdb(Path(tmp) / "in.pdb", spec["stem"], spec.get("residues"))

        t0 = time.perf_counter()
        chain, protid = retrieve_chain(path)
        t_parse = time.perf_counter() - t0

        t0 = time.perf_counter()
        index, numbering, protid, _ = get_cmap(chain, level="chain", **params)
        t_cmap = time.perf_counter() - t0

        t0 = time.perf_counter()
        frames = spec.get("frames", 1)
        for _ in range(frames):
            get_matrix(index, protid)
        t_matrix = time.perf_counter() - t0

    return {
        **spec,
        "n_residues": len(numbering),
        "n_contacts": len(index),
        "parse_s": round(t_parse, 4),
        "get_cmap_s": round(t_cmap, 4),
        "get_matrix_s": round(t_matrix, 4),
        "total_s": round(t_parse + t_cmap + t_matrix, 4),
        "peak_rss_mb": round(peak_rss_mb(), 1),
    }


def points() -> list[dict]:
    sweep = [{"sweep": "residues", "stem": "1crn", "residues": None, "cutoff": 4.5, "frames": 1}]
    sweep += [
        {"sweep": "residues", "stem": "1ubq", "residues": n, "cutoff": 4.5, "frames": 1}
        for n in (20, 40, 60, None)
    ]
    sweep += [
        {"sweep": "contacts", "stem": "1ubq", "residues": None, "cutoff": c, "frames": 1}
        for c in (5.0, 6.0, 7.0, 8.0)
    ]
    sweep += [
        {"sweep": "frames", "stem": "1ubq", "residues": None, "cutoff": 4.5, "frames": f}
        for f in (10, 50, 100)
    ]

    return sweep


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--point", help=argparse.SUPPRESS)

    args = parser.parse_args(argv[1:])
    if args.point:
        print(json.dumps(run_point(json.loads(args.point))))
        return 0

    rows = []
    for spec in points():
        proc = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--point", json.dumps(spec)],
            capture_output=True, text=True, check=False,
        )
        if proc.returncode != 0:
            print(f"FAIL {spec}: {proc.stderr.strip()[-400:]}")
            return 1

        row = json.loads(proc.stdout.strip().splitlines()[-1])
        if row["peak_rss_mb"] <= 0:
            print(f"FAIL {spec}: peak RSS came back as {row['peak_rss_mb']}; refusing to publish it")
            return 1

        rows.append(row)

        print(f"  {row['sweep']:<9} {row['stem']:<5} res={row['n_residues']:>4} "
              f"contacts={row['n_contacts']:>5} frames={row['frames']:>4} "
              f"total={row['total_s']:>7.3f}s peak={row['peak_rss_mb']:>7.1f}MB")

    columns = ["sweep", "stem", "cutoff", "frames", "n_residues", "n_contacts",
               "parse_s", "get_cmap_s", "get_matrix_s", "total_s", "peak_rss_mb"]
    RESULTS.write_text(
        ",".join(columns) + "\n"
        + "\n".join(",".join(str(row[c]) for c in columns) for row in rows) + "\n",
        encoding="utf-8", newline="",
    )

    print(f"\nwrote {RESULTS.relative_to(REPO)} ({len(rows)} points)")
    print(f"host: {platform.platform()} | {platform.processor()} | python {platform.python_version()}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
