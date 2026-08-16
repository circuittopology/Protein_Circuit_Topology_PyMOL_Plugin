# Executable capsule for the Protein Circuit Topology PyMOL plugin.
#
# Run with one command to reproduce:
#     docker run --rm ghcr.io/circuittopology/proteinct-plugin:<tag>
#
# To save outputs:
#     docker run --rm -v "$PWD/out:/out" -e CT_OUTDIR=/out ghcr.io/circuittopology/proteinct-plugin:<tag>
FROM mambaorg/micromamba:1.5.8

USER root
WORKDIR /opt/proteinct

# Installed before the conda layer so that layer stays cached when this list changes.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libegl1 \
        libxkbcommon0 \
        libdbus-1-3 \
        libfontconfig1 \
        libxrender1 \
        libxext6 \
        libsm6 \
        libice6 \
        libxi6 \
    && rm -rf /var/lib/apt/lists/*

COPY ci/environment.yml /tmp/environment.yml
RUN micromamba install -y -n base -f /tmp/environment.yml \
    && micromamba clean --all --yes

ENV PATH=/opt/conda/bin:$PATH \
    QT_QPA_PLATFORM=offscreen \
    MPLBACKEND=Agg \
    PYTHONUTF8=1 \
    PYTHONHASHSEED=0 \
    CT_REPO=/opt/proteinct \
    CT_OUTDIR=/tmp/reproduce_out

COPY analysis/           analysis/
COPY functions/          functions/
COPY tabs/               tabs/
COPY utils/              utils/
COPY __init__.py gui_class.py initialization_checks.py setup.py requirements.yml ./
COPY reproduce.pml       ./
COPY tests/data/         tests/data/

RUN pymol -cqy reproduce.pml && rm -rf /tmp/reproduce_out

ENTRYPOINT ["pymol", "-cqy", "reproduce.pml"]
