#!/usr/bin/env bash
#
# 把改动发布到 GitHub Pages
#
#   ./deploy.sh              用默认提交信息
#   ./deploy.sh "改了文案"    自定义提交信息
#
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

MSG="${1:-更新页面}"

if [ -n "$(git status --porcelain)" ]; then
  git add -A
  git commit -q -m "$MSG"
  echo "✓ 已提交：$MSG"
else
  echo "· 没有新改动，直接发布当前状态"
fi

echo "→ 推送 main ..."
git push -q origin main

echo "→ 推送 gh-pages（GitHub Pages 从这条分支发布）..."
git push -q -f origin main:gh-pages

echo
echo "✓ 发布完成，约 1 分钟后生效："
echo "  https://tavis-jiang.github.io/roux/"
