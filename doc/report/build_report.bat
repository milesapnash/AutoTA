@echo off

REM Builds the report PDF (main.pdf) from the LaTeX source in this directory.
REM Requires latexmk with biber, Pygments (for minted) and Inkscape (for svg).

where latexmk >nul 2>&1
if %errorlevel% neq 0 (
    echo latexmk is not installed or not added to PATH.
    exit /b 1
)

where pygmentize >nul 2>&1
if %errorlevel% neq 0 (
    echo Pygments is not installed ^(pip install pygments^).
    exit /b 1
)

where inkscape >nul 2>&1
if %errorlevel% neq 0 (
    echo Inkscape is not installed or not added to PATH.
    exit /b 1
)

REM Run from the directory containing this script, whatever the caller's directory
cd /d "%~dp0"

REM -shell-escape is required by the minted and svg packages
latexmk -pdf -shell-escape -interaction=nonstopmode main.tex
if %errorlevel% neq 0 (
    echo Failed to build the report.
    exit /b 1
)

echo Report built: %cd%\main.pdf
