"""
Setuptools configuration for the Circuit Topology plugin package.

This file is used when packaging and installing the plugin via standard
Python packaging tools. It provides metadata and declares runtime
dependencies so that packaging tools can produce installers or wheels.

Note
----
- The `install_requires` list attempts to capture necessary runtime
  dependencies; environment-specific packaging (conda/pip) may be needed
  for system-provided packages such as `dssp`.
"""

from setuptools import setup, find_packages

# Setup for the plugin
setup(
    name="circuit_topology_lacdr",
    version="v0.0.1",
    description = "PyMOL plugin for Circuit Topology GUI",
    author="LACDR",
    packages=find_packages(),
    install_requires=['numpy', 'pandas', 'matplotlib', 'pyqt', 'biopython'],
)
