#!/usr/bin/env bash
# Put the demo back to its starting state.
# In a git clone of the demo: undo every change in this folder and delete every new file.
# In any other copy (for example a ZIP download): delete reports/ and runbooks/, and
# restore deploy/deployment.yaml. Git is never used outside a clone of this demo.
set -eu
cd "$(dirname "$0")/.."
[ -f catalog-info.yaml ] && [ -f scripts/deployment.original.yaml ] || { echo "Cannot find the demo folder"; exit 2; }

if git ls-files --error-unmatch catalog-info.yaml >/dev/null 2>&1; then
  git checkout -- .
  git clean -fdq -- .
  left=$(git status --porcelain --untracked-files=all -- . | wc -l | tr -d ' ')
  echo "RESET: $left changed files left"
  [ "$left" = 0 ]
else
  rm -rf reports runbooks
  cp scripts/deployment.original.yaml deploy/deployment.yaml
  echo "RESET: removed reports/ and runbooks/, restored deploy/deployment.yaml"
fi
