from setuptools import setup, find_packages

# Setup for the plugin
setup(
    name="circuit_topology_lacdr",
    version="0.0",
    description = "PyMOL plugin for Circuit Topology GUI",
    author="LACDR",
    packages=find_packages(),
    install_requires=['numpy', 'pandas', 'matplotlib', 'dssp', 
                      'scipy', 'pyqt', 'biopython',
                      'ipywidgets', 'pip']
)