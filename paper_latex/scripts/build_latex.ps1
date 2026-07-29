param(
    [string]$MainTex = "main.tex",
    [string]$OutputDirectory = "build"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command latexmk -ErrorAction SilentlyContinue)) {
    throw "latexmk was not found on PATH. Install TeX Live or MiKTeX and reopen the shell."
}

latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir="$OutputDirectory" "$MainTex"
