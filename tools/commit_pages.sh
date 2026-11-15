#!/bin/sh
# usage: tools/commit_pages.sh "<message suffix>"  — commits each changed page separately
cd "$(dirname "$0")/.." || exit 1
for f in *.html; do
  if [ -n "$(git status --porcelain -- "$f")" ]; then
    git add -- "$f" && git commit -q -m "page: ${f%.html} — $1

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && echo "committed $f"
  fi
done
