# Performance
Wall time and peak memory for the analysis pipeline, measured with `python benchmarks/run.py`.

## Hardware and environment
| | |
|---|---|
| CPU | Intel Core Ultra 7 (Family 6, Model 170, Stepping 4), x86-64 |
| OS | Windows 11 Pro, build 26200 |
| Python | 3.10.18 |
| PyMOL | 3.1.6.1 (Schrödinger) |
| numpy / pandas / biopython | 1.26.4 / 2.3.3 / 1.85 |

## Results
>[!NOTE]
> Results show time in seconds, memory in MB. Using default 4.5 Å / 5 contacts / 3 neighbours unless stated otherwise.

### By protein length
| Structure | Residues | Contacts | parse | get_cmap | get_matrix | total | peak RSS |
|---|---|---|---|---|---|---|---|
| 1UBQ (truncated) | 20 | 10 | 0.036 | 0.003 | 0.000 | 0.039 | 42.6 |
| 1UBQ (truncated) | 40 | 24 | 0.029 | 0.006 | 0.000 | 0.036 | 43.1 |
| 1CRN | 46 | 45 | 0.039 | 0.008 | 0.001 | 0.048 | 42.8 |
| 1UBQ (truncated) | 60 | 49 | 0.031 | 0.013 | 0.001 | 0.045 | 43.2 |
| 1UBQ | 76 | 72 | 0.037 | 0.016 | 0.001 | 0.054 | 43.7 |

### By contact count
The same 76 residues throughout (`1UBQ`); only the distance cut-off changes, so this isolates scaling in the
number of contacts *C* from scaling in chain length.

| Cut-off (Å) | Contacts | get_cmap | get_matrix | total | peak RSS |
|---|---|---|---|---|---|
| 4.5 | 72 | 0.016 | 0.001 | 0.054 | 43.7 |
| 5.0 | 123 | 0.021 | 0.004 | 0.058 | 44.5 |
| 6.0 | 181 | 0.033 | 0.009 | 0.078 | 44.3 |
| 7.0 | 241 | 0.048 | 0.017 | 0.099 | 45.5 |
| 8.0 | 340 | 0.072 | 0.033 | 0.137 | 46.3 |

### By frame count
| Frames | total | peak RSS |
|---|---|---|
| 10 | 0.062 | 43.7 |
| 50 | 0.121 | 43.9 |
| 100 | 0.208 | 43.7 |

## Implications
- Typical single structure analysis is **well under a tenth of a second**.
- Computational cost is driven by contact count, not residue count directly. Contact count grows sharply with
  the distance cut-off. Raising the cut-off from 4.5 Å to 8 Å is a 2.5× slowdown on the same protein.
- Memory is nearly constant at ~43 MB regardless of the workload; nothing accumulates
  across frames.
