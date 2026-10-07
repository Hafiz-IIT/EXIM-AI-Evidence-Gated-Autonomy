# Prepare a clean arXiv source bundle from the repository.

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$out = Join-Path $root "dist"
$tmp = Join-Path $out "arxiv-source"

Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force $tmp | Out-Null

Copy-Item (Join-Path $root "paper/main.tex") $tmp
Copy-Item (Join-Path $root "paper/references.bib") $tmp

$zip = Join-Path $out "ega-v1-arxiv-source.zip"
Remove-Item $zip -Force -ErrorAction SilentlyContinue
Compress-Archive -Path (Join-Path $tmp "*") -DestinationPath $zip

Write-Host "Prepared: $zip"
Write-Host "Review the compiled PDF and arXiv metadata before uploading."
