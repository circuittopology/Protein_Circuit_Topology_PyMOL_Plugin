## Running tests

```bash
micromamba create -f ci/environment.yml -n proteinct-ci
micromamba activate proteinct-ci

pytest
```

The upstream-parity tests need a submodule. Without it they **skip** (green, but they prove nothing):

```bash
git submodule update --init
pytest tests/test_upstream_parity.py
```

```bash
pymol -cqy reproduce.pml
bash ci/build_plugin_zip.sh proteinct_plugin.zip
python ci/install_plugin_headless.py proteinct_plugin.zip /tmp/plugs # installs it via PyMOL's Plugin Manager
```

## `tests/data/`

`inputs/` holds `1crn.pdb` and `1ubq.pdb` — unmodified RCSB downloads (CC0). `expected/` holds the
reference CSVs, all generated at `cutoff_distance=4.5`, `cutoff_numcontacts=5`, `exclude_neighbour=3`
(`conftest.PARAMS`).

`1pnj.pdb` is read from the submodule during parity tests.
