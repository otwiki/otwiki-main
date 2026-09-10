#!/usr/bin/env bash
# Mirror the checked site without rewriting the existing gh-pages history.
set -euo pipefail

site_dir="$(cd "${1:?Pass the rendered site directory}" && pwd)"
test -f "$site_dir/index.html"
test "$(cat "$site_dir/CNAME")" = 'www.otwiki.xyz'
test -f "$site_dir/.nojekyll"

git fetch origin gh-pages
publish_dir="$(mktemp -d)"
git worktree add --detach "$publish_dir" FETCH_HEAD
trap 'git worktree remove --force "$publish_dir"' EXIT
rsync -a --delete --exclude='.git' "$site_dir/" "$publish_dir/"
git -C "$publish_dir" add --all
if ! git -C "$publish_dir" diff --cached --quiet; then
  git -C "$publish_dir" -c user.name='github-actions[bot]' \
    -c user.email='41898282+github-actions[bot]@users.noreply.github.com' \
    commit -m "Publish wiki from ${GITHUB_SHA:-$(git rev-parse HEAD)}"
  git -C "$publish_dir" push origin HEAD:gh-pages
fi
