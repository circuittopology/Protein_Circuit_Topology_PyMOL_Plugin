# Circuit Topology Plugin for PyMOL

## Overview

This repository contains a PyMOL plugin for analyzing protein circuit topology (CT) via a graphical user interface (GUI). It packages the [ProteinCT](https://github.com/circuittopology) library and additional tools into an easy-to-install and easy-to-use plugin, allowing researchers to explore protein topology without scripting.

## Key Features

- **User-friendly GUI** – An intuitive graphical interface that simplifies interaction with the underlying ProteinCT tool, removing the need for scripting.
- **Full PyMOL integration** – Seamless interaction with PyMOL's API for loading, visualizing, and analyzing protein structures directly within PyMOL.
- **Automatic dependency installation** – On first launch the plugin attempts to install its required Python packages automatically.
- **Supported file formats** – Works with PDB, CIF, and XTC files.
- **Single & multi-file analysis** – Analyze individual structures, single frames, or batch-process multiple files at once.
- **Visualization** - generate circuit and matrix plots, visualize CT contacts on PyMOL's objects.
- **Export capabilities** – Export contact maps, matrices, and per-structure counts to common formats.

## Installation

### 1. Install PyMOL

Download the **PyMOL 3.1.6.1** installer for your platform (Windows / Linux / macOS) from Pymol's website ([https://www.pymol.org/](https://www.pymol.org/)). Previous versions can be found at:

> <https://storage.googleapis.com/pymol-storage/installers/index.html>

During setup, **install PyMOL for the current user only** (select **"Just Me (recommended)"**). This ensures the plugin's automatic dependency installer has the necessary write permissions.

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

## Citation

If you use this plugin in your research, please cite the following article:

> **PyMOL plugin for Protein Circuit Topology**
>
> Matīss Dimiņš, Alexander Bazba, Ádám Mogyorósi, Ella Kennon, Tomás Díaz Fiol, Leïla Aïkili Hagen, Vahid Sheikhassani, Vasily Akulov, Alireza Mashaghi\*

<details>
<summary>Abstract</summary>

Circuit Topology (CT) is a fundamental property of folded polymer chains and provides a unique and powerful topological framework for analysis of proteins, with applications in functional annotation, disease marker identification, protein engineering, and drug development. While an open-source Python-based implementation of the framework, called ProteinCT, exists, its usability is limited for researchers unfamiliar with scripting environments. Here, we present the ProteinCT tool as a plugin for the molecular visualization platform PyMOL, packaged together with a graphical user interface (GUI), easy automatic installation, and novel features developed through strong integration with PyMOL's application programming interface (API). Our plugin packs the existing ProteinCT tool and its features into a .zip plugin for PyMOL that can be easily imported and automatically installed. A clear and visually intuitive GUI is included as part of the plugin. Our solution aims to connect the underlying functionality of the ProteinCT tool with PyMOL. This will provide protein researchers a tool for analysing protein topology. By analysing a representative protein trajectory, it is verified that the original functionality of the ProteinCT tool is retained in this plugin; that the GUI is functional, easy to use, and visually clear; and that additional functionality has been seamlessly integrated with PyMOL's API, thus making protein circuit topology widely accessible to a broad range of users in structural biology and related fields.

</details>

## Dependency Constraints

The table below lists the pinned dependency versions that have been verified to work with this plugin. The [requirements.yml](requirements.yml) file has relaxed dependency constraints in case you do not stick

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