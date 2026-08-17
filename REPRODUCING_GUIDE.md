# Reproducing the published results
Every CSV produced is compared against the reference outputs committed in `tests/data/expected/`, and the run **exits non-zero if any value moved**.

## 1. Run with one command via Docker
```bash
docker run --rm ghcr.io/circuittopology/proteinct-plugin:<tag>
```

To keep the artefacts:
```bash
mkdir out
docker run --rm -v "$PWD/out:/out" -e CT_OUTDIR=/out ghcr.io/circuittopology/proteinct-plugin:<tag>
```

The image is built by [`.github/workflows/capsule.yml`](.github/workflows/capsule.yml) from [`capsule/Dockerfile`](capsule/Dockerfile).  

During the build, [`reproduce.pml`](reproduce.pml) runs as a build step, so a built image indicates the image reproduced.  

## 2. Local conda environment
```bash
# Version-pinned:
micromamba create -f ci/environment.yml -n proteinct-ci
micromamba activate proteinct-ci

# Or byte-identical, from the lock file for your platform:
conda create --name proteinct-ci --file ci/conda-lock-linux-64.txt   # or -win-64

pymol -cqy reproduce.pml
```

[`ci/environment.yml`](ci/environment.yml) pins versions; the lock files pin exact builds.  

Two platforms are committed, and they were produced differently.
[`ci/conda-lock-linux-64.txt`](ci/conda-lock-linux-64.txt) was exported from a real installed
environment, so all 221 entries carry md5 checksums.
[`ci/conda-lock-win-64.txt`](ci/conda-lock-win-64.txt) came from a dry-run conda solve, which conda cannot attach checksums to, so its 162 entries are URL-only.  

CI also exports a checksummed lock as a build artifact (`conda-lock-<os>`) on every run.

Moreover, you can produce one yourself from an installed environment:
```bash
python ci/make_lock.py --from-prefix "$CONDA_PREFIX"
```

## 3. Inside an existing PyMOL
```
@reproduce.pml
```

Requires numpy, pandas, matplotlib and biopython in PyMOL's environment. See the manual-installation section of the [`README.md`](README.md).
