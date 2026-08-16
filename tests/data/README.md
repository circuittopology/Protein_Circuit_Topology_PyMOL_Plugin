## Inputs
| File | PDB ID | Residues | Chains | Source |
|---|---|---|---|---|
| `1crn.pdb` | 1CRN | 46 | A | <https://files.rcsb.org/download/1CRN.pdb> |
| `1ubq.pdb` | 1UBQ | 76 | A | <https://files.rcsb.org/download/1UBQ.pdb> |

## Analysis parameters
| Parameter | Value |
|---|---|
| `cutoff_distance` | 4.5 Å |
| `cutoff_numcontacts` | 5 |
| `exclude_neighbour` | 3 |
| contact level | `chain` (both fixtures are single-chain) |

Resulting contact counts:
* **1CRN → 45 contacts**
* **1UBQ → 72 contacts**

**Changing any of thea analysis parameters invalidates every expected output.**

## Expected outputs
| Directory | Produced by | Files |
|---|---|---|
| `expected/single_1crn/` | Single-File Analysis tab | `1crn_chain_A_cmap3.csv`, `1crn_mat.csv` |
| `expected/single_1ubq/` | Single-File Analysis tab | `1ubq_chain_A_cmap3.csv`, `1ubq_mat.csv` |
| `expected/local_1ubq/` | Local Circuit Topology tab, residue 10 | `1ubq_chain_A_cmap3.csv`, `1ubq_chain_A_mat.csv` |
| `expected/multi/` | Multi-File Analysis tab over `inputs/` | `psxresults.csv` |

## Environment used to generate these files
| Component | Version |
|---|---|
| PyMOL | 3.1.6.1 (Schrödinger channel) |
| Python | 3.10.18 |
| numpy | 1.26.4 |
| pandas | 2.3.3 |
| matplotlib | 3.9.1 |
| biopython | 1.85 |
| OS | Windows 11 Pro, build 26200, x86-64 |

## Regenerating

```
pytest --update-expected
```
