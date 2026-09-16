# Reproducing the published results
`reproduce.pml` analyses the three bundled structures (1AKI, the paper's lysozyme example; 1CRN; 1UBQ)
with the default contact criterion (4.5 Å, at least 5 atom-atom pairs, more than 3 residues apart,
heavy atoms only). Every CSV produced is compared against the reference outputs committed in
`tests/data/expected/`, the CT folding scores are checked against pinned values, and the run
**exits non-zero if any value moved**. It also writes the figures of the paper (Figs. 3, 4, 5 and 7,
all 1AKI) with enlarged fonts to `<output>/figures/paper/`.

The version described in the paper is the `v0.0.3` tag; replace the tag below to reproduce another release.

## 1. Run with one command via Docker
```bash
docker run --rm ghcr.io/circuittopology/proteinct-plugin:v0.0.3
```

To keep the artefacts:
```bash
mkdir out
docker run --rm -v "$PWD/out:/out" -e CT_OUTDIR=/out ghcr.io/circuittopology/proteinct-plugin:v0.0.3
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
