param([string]$OutputDirectory = "build")

$ErrorActionPreference = "Stop"

if (-not (Get-Command latexmk -ErrorAction SilentlyContinue)) {
    throw "latexmk was not found on PATH. Install TeX Live or MiKTeX and reopen the shell."
}

$paperRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$outputPath = if ([IO.Path]::IsPathRooted($OutputDirectory)) {
    $OutputDirectory
} else {
    Join-Path $paperRoot $OutputDirectory
}

New-Item -ItemType Directory -Force -Path $outputPath | Out-Null
Push-Location $paperRoot
try {
    foreach ($target in @("main.tex", "supplementary.tex", "cover_letter.tex")) {
        & latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir="$outputPath" "$target"
        if ($LASTEXITCODE -ne 0) {
            throw "LaTeX compilation failed for $target (exit code $LASTEXITCODE)."
        }
    }

    Copy-Item (Join-Path $outputPath "main.pdf") "paper_manuscript_latex.pdf" -Force
    Copy-Item (Join-Path $outputPath "supplementary.pdf") "paper_supplementary_latex.pdf" -Force
    Copy-Item (Join-Path $outputPath "cover_letter.pdf") "cover_letter.pdf" -Force
} finally {
    Pop-Location
}
