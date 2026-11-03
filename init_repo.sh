#!/bin/sh
# Создаёт git-репозиторий с 5 коммитами (по одному на этап) от вашего имени
# (берётся из git config user.name / user.email).
# Использование:  sh init_repo.sh https://github.com/ЛОГИН/РЕПО.git
set -e
[ -n "$(git config user.name)" ] && [ -n "$(git config user.email)" ] || {
  echo "Сначала: git config --global user.name \"Имя\"; git config --global user.email you@example.com"; exit 1; }
[ -d .git ] && { echo "Репозиторий уже инициализирован"; exit 1; }
git init -q && git branch -M main

git add depviz/__init__.py depviz/errors.py depviz/config.py depviz/cli.py depviz/__main__.py main.py .gitignore
git commit -q -m "feat: stage 1 - CLI prototype with configuration and error handling"

git add depviz/npm.py depviz/semver.py
git commit -q -m "feat: stage 2 - collect direct npm dependencies from registry"

git add depviz/graph.py depviz/testrepo.py examples tests
git commit -q -m "feat: stage 3 - recursive DFS dependency graph, cycles, test repository mode"

git add depviz/loadorder.py
git commit -q -m "feat: stage 4 - dependency load order"

git add depviz/mermaid.py depviz/render.py depviz/asciitree.py README.md init_repo.sh
git commit -q -m "feat: stage 5 - Mermaid, PNG and ASCII tree visualization"

git log --oneline
if [ -n "$1" ]; then
  git remote add origin "$1"
  git push -u origin main
else
  echo "Дальше: git remote add origin <URL> && git push -u origin main"
fi
