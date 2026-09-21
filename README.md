# Circuit Topology Plugin for PyMOL

## Overview

This repository contains a PyMOL plugin for analyzing protein circuit topology (CT) via a graphical user interface (GUI). It packages the [ProteinCT](https://github.com/circuittopology) library and additional tools into an easy-to-install and easy-to-use plugin, allowing researchers to explore protein topology without scripting.

## Key Features

- **User-friendly GUI** – An intuitive graphical interface that simplifies interaction with the underlying ProteinCT tool, removing the need for scripting.
- **Full PyMOL integration** – Seamless interaction with PyMOL's API for loading, visualizing, and analyzing protein structures directly within PyMOL.
- **Automatic dependency installation** – On first launch the plugin attempts to install its required Python packages automatically.
- **Supported file formats** – PDB/mmCIF structures and XTC trajectories.
- **Single & multi-file analysis** – Analyze individual structures, single frames, or batch-process multiple files at once.
- **Visualization** - generate circuit and matrix plots, and colour PyMOL objects by each residue's participation in Series (S), Parallel (P) and Cross (X) relations.
- **Export capabilities** – Export contact maps, relation matrices, and per-structure P, S, X relation counts as CSV.
- **Explicit contact criterion** – 4.5 Å, at least 5 atom-atom pairs, more than 3 residues apart, heavy atoms only by default; a "Count hydrogen atoms (ProteinCT-identical)" option reproduces the reference implementation on hydrogen-bearing files. Multi-chain objects are analysed as a whole model: inter-chain contact pairs are included and relations involving them use the I/T/L vocabulary (see the manual's Methods specification).

## Installation

### 1. Install PyMOL

Download the **PyMOL 3.1.6.1** installer for your platform (Windows / Linux / macOS) from Pymol's website ([https://www.pymol.org/](https://www.pymol.org/)). Previous versions can be found at:

> <https://storage.googleapis.com/pymol-storage/installers/index.html>

During setup, **install PyMOL for the current user only** (select **"Just Me (recommended)"**). This ensures the plugin's automatic dependency installer has the necessary write permissions. If you do install PyMOL for **All Users (requires admin privileges)**, ensure you run PyMOL as administrator to increase the chances of automatic conda package installation.

### 2. Register file extensions

When PyMOL prompts you to register file extensions, select **"Register Recommended"**. For this plugin you will primarily work with **PDB**, **CIF**, and **XTC** files.

### 3. Download the plugin

Download the latest plugin release ZIP (`.zip`) file directly from GitHub Releases:

> Latest plugin ZIP: <https://github.com/circuittopology/Protein_Circuit_Topology_PyMOL_Plugin/releases/latest/download/protein-circuit-topology-pymol-plugin.zip>

If you need a specific tagged version instead of the latest release, use the Releases page:

> <https://github.com/circuittopology/Protein_Circuit_Topology_PyMOL_Plugin/releases>

### 4. Install the plugin in PyMOL

1. Open PyMOL.
2. Navigate to **Plugin → Plugin Manager → Install New Plugin → Choose File**.
3. Select the `.zip` file you downloaded in the previous step.
4. Wait a few seconds for the plugin to install and set up its dependencies.

### 5. Launch the plugin

Once installation is complete, open the plugin's GUI from:

> **Plugin → Protein Circuit Topology Plugin**

### What the automatic installer changes in the PyMOL conda environment
- It locates the conda of the running PyMOL — `CONDA_EXE` first, then the usual paths under
  `sys.prefix`, then `conda` on `PATH`.
- It runs, once:
  ```
  <conda> install --yes --freeze-installed --prefix <PyMOL's sys.prefix> \
      python==<installed version> pymol==<installed version> conda-forge::<each missing package>
  ```
- **This updates PyMOL's own conda environment in place.** It does not create a new environment and
  does not touch any other environment on your system. Packages come from `conda-forge`.
- No administrator rights are needed if PyMOL was installed "Just Me". If it was installed
  system-wide, the update will fail and the plugin prints the exact command to run yourself from an
  elevated terminal.
- Nothing is uninstalled or downgraded beyond what conda needs to satisfy the version ranges in
  [`requirements.yml`](requirements.yml).

### Manual installation
If you would rather not let the plugin touch your environment, install the dependencies yourself **before** loading the plugin. It only auto-installs what is missing.
```bash
# Find the prefix and the versions to pin:
#   python -c "import sys, pymol; print(sys.prefix, sys.version.split()[0], pymol.cmd.get_version()[0])"
conda install --yes --freeze-installed --prefix <PyMOL's sys.prefix> \
    python==<installed version> pymol==<installed version> \
    "conda-forge::numpy>=1.23,<2" "conda-forge::pandas>=2.0,<3" \
    "conda-forge::matplotlib>=3.7,<4" "conda-forge::biopython>=1.80,<2"
```

For a bit-for-bit reproduction of the environment the reference outputs were generated in, use the
lock file rather than the ranges:

```bash
conda create --name proteinct --file ci/conda-lock-<platform>.txt
```

## Reproducing the published outputs
```bash
pymol -cqy reproduce.pml
```

Runs the full pipeline on the bundled example structures (1AKI, the lysozyme example of the paper; 1CRN;
1UBQ), **compares every CSV it produces against the committed reference outputs** in `tests/data/expected/`,
checks the CT folding scores, and writes the paper's figures (Figs. 3, 4, 5 and 7) with enlarged fonts to
`reproduce_out/figures/paper/`. It exits non-zero if any number moved. See [REPRODUCING_GUIDE.md](REPRODUCING_GUIDE.md)
for the Docker and conda routes.

## Performance
Wall time, memory and trajectory disk usage, with the hardware stated:
[benchmarks/README.md](benchmarks/README.md).

## API Documentation
You can read the full API documentation [here](documentation/api_documentation.pdf).

## Manual
A guide on how to use the GUI is available [here](documentation/CircuitTopologyManual.pdf).

## Citation

If you use this plugin in your research, please cite the following article:

> **PyMOL plugin for Protein Circuit Topology**
>
> Matīss Dimiņš, Alexander Bazba, Ádám Mogyorósi, Ella Kennon, Tomás Díaz Fiol, Leïla Aïkili Hagen, Vahid Sheikhassani, Vasily Akulov, Alireza Mashaghi\*

The version described in the paper is release **v0.0.4**:
<https://github.com/circuittopology/Protein_Circuit_Topology_PyMOL_Plugin/releases/tag/v0.0.4>
(commit `92ed0ede471c8aec9dffea58a9ff0bf5141ea81a`; repository archive on Zenodo `10.5281/zenodo.22858259`, release artefacts on Zenodo `10.5281/zenodo.22879946`).

<details>
<summary>Abstract</summary>

Circuit Topology (CT) provides a fundamental framework for analysing folded polymer chains, with applications in functional annotation, protein engineering and drug development. We present a protein CT analysis plugin for PyMOL v3.1.6.1 with a graphical user interface (GUI), automatic installation, and novel features developed through integration with PyMOL's application programming interface (API). The plugin integrates various previously developed CT methodologies for studying structured proteins and their complexes as well as the dynamics of disordered proteins. Analysis of a representative protein and a molecular dynamics trajectory demonstrates the plugin's three analysis modes and their outputs. The plugin reproduces the reference ProteinCT implementation exactly on the structures tested, and is distributed with a versioned release, a pinned environment and a one-command reproduction of every static result reported here.

</details>

## Dependency Constraints

The table below lists the pinned dependency versions that have been verified to work with this plugin. The [requirements.yml](requirements.yml) file has relaxed dependency constraints in case you do not follow the installation guide 1:1.

```yml
dependencies:
  - conda-forge::python=3.10.18
  - conda-forge::pyqt=5.15.11
  - conda-forge::qt-main=5.15.15
  - conda-forge::pyqt5-sip=12.17.0
  - conda-forge::biopython=1.85
  - conda-forge::numpy=1.26.4
  - conda-forge::pandas=2.3.3
  - conda-forge::matplotlib=3.9.1
  - schrodinger::pymol=3.1.6.1
  - schrodinger::pymol-bundle=3.1.6.1
```
