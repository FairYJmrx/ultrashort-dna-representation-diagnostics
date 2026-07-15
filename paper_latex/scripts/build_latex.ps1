param(
    [string]$MainTex = "main.tex",
    [string]$OutputDirectory = "build"
)

$ErrorActionPreference = "Stop"

$miktexBin = "C:\Users\24409\AppData\Local\Programs\MiKTeX\miktex\bin\x64"
$perlBin = "C:\Strawberry\perl\bin"
$perlCBin = "C:\Strawberry\c\bin"
$perlSiteBin = "C:\Strawberry\perl\site\bin"

$env:Path = "$perlBin;$perlCBin;$perlSiteBin;$miktexBin;$env:Path"

latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir="$OutputDirectory" "$MainTex"
