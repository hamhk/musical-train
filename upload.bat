@echo off
chcp 65001 >nul
cd /d "%~dp0"
where git >nul 2>nul
if errorlevel 1 (
  echo Git ne ustanovlen. Skachaite: https://git-scm.com/download/win
  pause
  exit /b 1
)
set /p NAME=Vashe imya: 
set /p EMAIL=Vasha pochta: 
set /p URL=Ssylka na pustoj repozitorij GitHub: 
git config user.name "%NAME%"
git config user.email "%EMAIL%"
if exist .git rmdir /s /q .git
git init
git branch -M main
git add depviz/__init__.py depviz/errors.py depviz/config.py depviz/cli.py depviz/__main__.py main.py .gitignore
git commit -m "feat: stage 1 - CLI prototype with configuration and error handling"
git add depviz/npm.py depviz/semver.py
git commit -m "feat: stage 2 - collect direct npm dependencies from registry"
git add depviz/graph.py depviz/testrepo.py examples tests
git commit -m "feat: stage 3 - recursive DFS dependency graph, cycles, test repository mode"
git add depviz/loadorder.py
git commit -m "feat: stage 4 - dependency load order"
git add depviz/mermaid.py depviz/render.py depviz/asciitree.py README.md init_repo.sh upload.bat
git commit -m "feat: stage 5 - Mermaid, PNG and ASCII tree visualization"
git remote add origin %URL%
git push -u origin main
echo.
echo Gotovo. Proverte repozitorij na GitHub.
pause
