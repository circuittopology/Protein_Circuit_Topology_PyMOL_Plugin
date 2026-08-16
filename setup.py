from setuptools import find_packages, setup

setup(
    name="circuit_topology_lacdr",
    version="v0.0.2",
    description="PyMOL plugin for Circuit Topology GUI",
    author="LACDR",
    packages=find_packages(),
    package_data={"functions.calculating": ["matrix_potential.txt"]},
    install_requires=["numpy", "pandas", "matplotlib", "biopython"],
    extras_require={"gui": ["PyQt5"]},
    python_requires=">=3.10",
)
