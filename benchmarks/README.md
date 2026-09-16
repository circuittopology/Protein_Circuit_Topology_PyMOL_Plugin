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
> Measured with plugin v0.0.3 on 6 September 2026 with the default heavy-atom contact criterion (1CRN and 1UBQ carry
> no hydrogens, so the hydrogen setting does not change these numbers).

### By protein length
| Structure | Residues | Contacts | parse | get_cmap | get_matrix | total | peak RSS |
|---|---|---|---|---|---|---|---|
| 1UBQ (truncated) | 20 | 10 | 0.029 | 0.003 | 0.000 | 0.032 | 42.4 |
| 1UBQ (truncated) | 40 | 24 | 0.023 | 0.006 | 0.000 | 0.029 | 42.7 |
| 1CRN | 46 | 45 | 0.023 | 0.008 | 0.001 | 0.032 | 42.7 |
| 1UBQ (truncated) | 60 | 49 | 0.025 | 0.012 | 0.001 | 0.038 | 43.2 |
| 1UBQ | 76 | 72 | 0.027 | 0.015 | 0.001 | 0.043 | 43.7 |

### By contact count
The same 76 residues throughout (`1UBQ`); only the distance cut-off changes, so this isolates scaling in the
number of contacts *C* from scaling in chain length.

| Cut-off (Å) | Contacts | get_cmap | get_matrix | total | peak RSS |
|---|---|---|---|---|---|
| 4.5 | 72 | 0.015 | 0.001 | 0.043 | 43.7 |
| 5.0 | 123 | 0.022 | 0.004 | 0.053 | 43.9 |
| 6.0 | 181 | 0.034 | 0.009 | 0.070 | 44.5 |
| 7.0 | 241 | 0.061 | 0.019 | 0.109 | 45.2 |
| 8.0 | 340 | 0.074 | 0.033 | 0.135 | 46.5 |

### By frame count
| Frames | total | peak RSS |
|---|---|---|
| 10 | 0.056 | 43.4 |
| 50 | 0.115 | 43.6 |
| 100 | 0.194 | 43.6 |

## Implications
- Typical single structure analysis is **well under a tenth of a second**.
- Computational cost is driven by contact count, not residue count directly. Contact count grows sharply with
  the distance cut-off. Raising the cut-off from 4.5 Å to 8 Å is roughly a 3× slowdown on the same protein.
- Memory is nearly constant at ~43 MB regardless of the workload; nothing accumulates
  across frames. Whole-trajectory *colouring* is the one exception — see below.

## Trajectory colouring memory
Colouring a whole trajectory by relation type is the only operation whose memory grows with the
trajectory. `cmd.split_states` creates one PyMOL object per state, all alive simultaneously, colours
each, then `cmd.join_states` merges them into `<object>_topo`. Measured on 1UBQ (602 polymer atoms),
resident set sampled at three points:

| States | objects | after load | after `split_states` | after join + delete |
|---|---|---|---|---|
| 10 | 1 → 11 → 2 | 81.7 MB | 101.0 | 137.0 |
| 50 | 1 → 51 → 2 | 119.1 MB | 202.3 | 378.0 |
| 200 | 1 → 201 → 2 | 258.8 MB | 570.8 | 1279.1 |
