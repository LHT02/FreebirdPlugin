param(
    [string]$BlenderRoot = 'C:\blender\software\stable\blender-3.6.23-lts.e467db79ca8c',
    [string]$FreebirdRoot = "$env:APPDATA\Blender Foundation\Blender\3.6\scripts\addons\freebird_xr"
)

$ErrorActionPreference = 'Stop'
$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $BlenderRoot '3.6\python\bin\python.exe'
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "Blender Python was not found: $python"
}
if (-not (Test-Path -LiteralPath $FreebirdRoot -PathType Container)) {
    throw "Freebird source was not found: $FreebirdRoot"
}

Push-Location $projectRoot
try {
    & $python -m compileall -q freebird_curve_editor tests tools\verify_freebird_source.py
    if ($LASTEXITCODE -ne 0) { throw 'Python compilation failed' }

    & $python -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Unit tests failed' }

    & $python tools\verify_freebird_source.py $FreebirdRoot
    if ($LASTEXITCODE -ne 0) { throw 'Freebird source contract verification failed' }

    git diff --check
    if ($LASTEXITCODE -ne 0) { throw 'Git whitespace validation failed' }
}
finally {
    Pop-Location
}
