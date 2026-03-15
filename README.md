# Circuit-Topology Plugin for PyMOL 

## Brief overview

A PyMOL plugin for analyzing protein circuit topology (CT) with an intuitive graphical user interface (GUI). It packages the ProteinCT and additional tools into an easy-to-install plugin, fully integrated with PyMOL, allowing researchers to explore protein topology without scripting. Features include automatic installation, a visually clear GUI, and seamless interaction with PyMOL’s API, making protein circuit topology accessible to structural biology researchers and related fields.

## Key Features

- User-friendly GUI: Simplifies interaction with the original code
- Integration with PyMol: Ensures compatibility with PyMol
- Improved Usability: Enhances accessibility for researchers

## Getting Started

1. Download the circuit_topology_plugin package.
2. Open PyMol
3. Use the Plugin Manager to install the circuit_topology_plugin.zip file as a new plugin.
4. Start using it

## Citation
Users are requested to cite the following article: 

Article title: 
PyMOL plugin for Protein Circuit Topology
Authors:
Matīss Dimiņš, Alexander Bazba, Ádám Mogyorósi, Ella Kennon, Tomás Díaz Fiol, Leïla Aïkili Hagen, Vahid Sheikhassani, Vasily Akulov, Alireza Mashaghi*

Abstract
Circuit Topology (CT) is a fundamental property of folded polymer chains and provides a unique and powerful topological framework for analysis of proteins, with applications in functional annotation, disease marker identification, protein engineering, and drug development. While an open-source Python-based implementation of the framework, called ProteinCT, exists, its usability is limited for researchers unfamiliar with scripting environments. Here, we present the ProteinCT tool as a plugin for the molecular visualization platform PyMOL, packaged together with a graphical user interface (GUI), easy automatic installation, and novel features developed through strong integration with PyMOL’s application programming interface (API). Our plugin packs the existing ProteinCT tool and its features into a .zip plugin for PyMOL that can be easily imported and automatically installed. A clear and visually intuitive GUI is included as part of the plugin. Our solution aims to connect the underlying functionality of the ProteinCT tool with PyMOL. This will provide protein researchers a tool for analysing protein topology. By analysing a representative protein trajectory, it is verified that the original functionality of the ProteinCT tool is retained in this plugin; that the GUI is functional, easy to use, and visually clear; and that additional functionality has been seamlessly integrated with PyMOL’s API, thus making protein circuit topology widely accessible to a broad range of users in structural biology and related fields.

## Dependency constraints
Below you can find the dependency constraints for all the core packages used by PyMOL and the plugin.  
  
Currently these have been pinned to specific verified versions. These are very strict but could definitely be relaxed in the future.  
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