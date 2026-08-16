#!/usr/bin/env bash
#
# Build the plugin release ZIP.
set -euo pipefail

out="${1:?usage: build_plugin_zip.sh <output.zip> [git-ref]}"
ref="${2:-HEAD}"

if [ "${ref}" = "HEAD" ] && [ -n "$(git status --porcelain -- analysis functions tabs utils \
    __init__.py gui_class.py initialization_checks.py setup.py requirements.yml 2>/dev/null)" ]; then
  echo "WARNING: uncommitted changes to shipped files; this ZIP is HEAD, not your working tree." >&2
fi

git archive \
  --format=zip \
  --prefix=proteinct_plugin/ \
  --output="${out}" \
  "${ref}" \
  analysis \
  functions \
  tabs \
  utils \
  __init__.py \
  gui_class.py \
  initialization_checks.py \
  setup.py \
  requirements.yml \
  LICENSE \
  README.md

ls -l "${out}"
